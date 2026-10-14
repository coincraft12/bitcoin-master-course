"""3부 미니 과제 정답: 지갑 없이 Taproot 송금 완성하기 (s7-assign, s7-hint).

lib만으로 키 → P2TR 주소 → 서명 전 트랜잭션 → BIP341 서명 해시 → 조정된 개인키로 Schnorr 서명 → witness → 직렬화.

    python part3/lesson-31/assignment/solution/solution_taproot_send.py           # 노드 없이: 고정 키 + 가짜 UTXO로 끝까지 실행·자체 검증
    python part3/lesson-31/assignment/solution/solution_taproot_send.py --node    # regtest: 새 키 → miner 입금 → testmempoolaccept → sendrawtransaction

노드 없는 모드의 키는 공개 테스트 니모닉(abandon ×11 + about)의 m/86h/1h/0h/0/0이다. 실제 자금에 절대 쓰지 말 것.
--node 모드는 실행할 때마다 새 개인키를 만들고 regtest WIF를 출력한다(regtest 전용).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import secrets
from lib.ec import G, N, point_mul
from lib.hashes import dsha256
from lib.keys import new_private_key, p2tr_address, address_to_script_pubkey, wif
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import tagged_hash, output_key
from lib.tx import parse_tx, serialize_tx
from lib.sighash import taproot_sighash
from lib import schnorr

FEE_RATE = 5                       # sat/vB
SEND = 5_000_000                   # bob에게 0.05 BTC
DUST_P2TR = 330                    # 잔돈이 이보다 작으면 잔돈 출력 없이 수수료로 (5-3)


# ---- s7-hint 그대로 ----
def tweak_seckey(d0: int) -> int:
    P = point_mul(G, d0)
    d = d0 if P[1] % 2 == 0 else N - d0              # 짝수 y에 맞춤
    t = int.from_bytes(tagged_hash("TapTweak", P[0].to_bytes(32, "big")), "big")
    return (d + t) % N                                # Q의 패리티는 sign()이 처리


# ---- 01 키와 주소 ----
def p2tr_of(d0: int) -> tuple:
    """(내부키 x 32B, 출력키 Q 32B, regtest 주소)"""
    P_x = point_mul(G, d0)[0].to_bytes(32, "big")
    Q = output_key(P_x)                               # BIP86: 머클 루트 없이 조정
    return P_x, Q, p2tr_address(Q, hrp="bcrt")


# ---- 03 서명 전 트랜잭션 (잔돈 주의) ----
def build_unsigned_tx(utxo: dict, to_addr: str, amount: int, change_addr: str, fee_rate: int) -> dict:
    """utxo = {"txid", "vout", "value_sat", "scriptPubKey"(hex)}. 잔돈 = 입력 − 보낼 금액 − 수수료.

    P2TR 키 경로 서명은 기본 sighash면 언제나 64바이트라, 빈 서명 자리(64B)로 크기를 재면 vsize가 정확하다.
    """
    tx = {"version": 2, "locktime": 0,
          "vin": [{"txid": utxo["txid"], "vout": utxo["vout"], "scriptSig": "", "sequence": 0xfffffffd}],
          "vout": [{"value_sat": amount, "scriptPubKey": address_to_script_pubkey(to_addr).hex()},
                   {"value_sat": 0, "scriptPubKey": address_to_script_pubkey(change_addr).hex()}]}
    tx["vin"][0]["witness"] = ["00" * 64]                         # 크기 재기용 자리
    vsize = parse_tx(serialize_tx(tx).hex())["vsize"]
    fee = fee_rate * vsize
    change = utxo["value_sat"] - amount - fee
    if change < DUST_P2TR:                                        # 잔돈이 더스트면 출력 없이 수수료로
        tx["vout"].pop()
    else:
        tx["vout"][1]["value_sat"] = change
    del tx["vin"][0]["witness"]
    if utxo["value_sat"] - sum(o["value_sat"] for o in tx["vout"]) > 100 * fee:
        raise ValueError("수수료가 너무 크다 — 잔돈 출력을 확인 (5-3)")
    return tx


# ---- 04 서명 해시 → 조정된 개인키로 Schnorr 서명 ----
def sign_keypath(tx: dict, utxo: dict, d0: int, aux_rand: bytes) -> tuple:
    prevouts = [(utxo["value_sat"], bytes.fromhex(utxo["scriptPubKey"]))]
    msg = taproot_sighash(tx, prevouts, 0, 0x00)                  # DEFAULT → 64바이트 서명, hash_type 바이트 생략
    sig = schnorr.sign(msg, tweak_seckey(d0).to_bytes(32, "big"), aux_rand)
    return msg, sig


# ---- 05 witness를 붙여 직렬화 ----
def finalize(tx: dict, sig: bytes) -> str:
    tx["vin"][0]["witness"] = [sig.hex()]
    return serialize_tx(tx).hex()


def self_check(hexstr: str, utxo: dict, Q: bytes, msg: bytes, sig: bytes) -> dict:
    t = parse_tx(hexstr)
    fee = utxo["value_sat"] - sum(o["value_sat"] for o in t["vout"])
    checks = {
        "직렬화 왕복": serialize_tx(parse_tx(hexstr)).hex() == hexstr,
        "출력키 = 이전 출력 scriptPubKey": bytes.fromhex(utxo["scriptPubKey"]) == b"\x51\x20" + Q,
        "서명 해시 재계산 일치": taproot_sighash(t, [(utxo["value_sat"], bytes.fromhex(utxo["scriptPubKey"]))], 0, 0x00) == msg,
        "Schnorr 검증(출력키 Q)": schnorr.verify(msg, Q, sig),
        "witness 1항목 64B": [len(w) // 2 for w in t["vin"][0]["witness"]] == [64],
        f"수수료율 ≥ {FEE_RATE} sat/vB": fee >= FEE_RATE * t["vsize"],
    }
    for k, v in checks.items():
        print(f"  {k:<28} {v}")
    print(f"  txid {t['txid']}\n  wtxid {t['wtxid']}")
    print(f"  size {t['size']} · weight {t['weight']} · vsize {t['vsize']} · 수수료 {fee} sat")
    assert all(checks.values())
    return t


def offline():
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    d0, _ = derive_priv(seed, "m/86h/1h/0h/0/0")
    dc, _ = derive_priv(seed, "m/86h/1h/0h/1/0")                     # 잔돈용 키 (/1/ 체인)
    P_x, Q, addr = p2tr_of(d0)
    change_addr = p2tr_of(dc)[2]
    bob = "bcrt1qp7shgcwx3mpzgxjvff0d77vuhchcldzfxnktde"           # data/demo_txs.json의 bob (테스트 니모닉 m/84h/1h/1h/0/0)
    print("01 내부키", P_x.hex())
    print("   출력키", Q.hex())
    print("   주소  ", addr)
    utxo = {"txid": dsha256(b"part3 assignment fake utxo")[::-1].hex(), "vout": 0,
            "value_sat": 10_000_000, "scriptPubKey": address_to_script_pubkey(addr).hex()}
    print("02 (가짜 UTXO) miner가 0.1 BTC를 보냈다고 가정:", f"{utxo['txid']}:{utxo['vout']}", utxo["value_sat"], "sat")
    tx = build_unsigned_tx(utxo, bob, SEND, change_addr, FEE_RATE)
    print("03 서명 전:", serialize_tx(tx).hex())
    print("   출력", [(o["value_sat"], o["scriptPubKey"][:8] + "…") for o in tx["vout"]])
    msg, sig = sign_keypath(tx, utxo, d0, b"\x00" * 32)            # 재현용 고정 aux_rand (실제로는 secrets.token_bytes(32))
    print("04 서명 해시", msg.hex())
    print("   서명    ", sig.hex())
    hexstr = finalize(tx, sig)
    print("05 서명된 트랜잭션:", hexstr)
    print("자체 검증")
    self_check(hexstr, utxo, Q, msg, sig)
    print("노드 제출은 --node 모드 (testmempoolaccept → sendrawtransaction)")


def node():
    from lib.rpc import RPC, btc_to_sat
    rpc, miner, bob = RPC(), RPC(wallet="miner"), RPC(wallet="bob")
    d0, dc = new_private_key(), new_private_key()
    P_x, Q, addr = p2tr_of(d0)
    change_addr = p2tr_of(dc)[2]
    print("01 개인키 WIF (regtest 전용):", wif(d0, version=0xef))
    print("   주소", addr)
    txid = miner.sendtoaddress(addr, "0.1")
    miner.generatetoaddress(1, miner.getnewaddress())
    prev = rpc.getrawtransaction(txid, True)
    vout = next(o for o in prev["vout"] if o["scriptPubKey"].get("address") == addr)
    utxo = {"txid": txid, "vout": vout["n"], "value_sat": btc_to_sat(vout["value"]),
            "scriptPubKey": vout["scriptPubKey"]["hex"]}
    print("02 받은 코인", f"{txid}:{vout['n']}", utxo["value_sat"], "sat")
    tx = build_unsigned_tx(utxo, bob.getnewaddress("", "bech32"), SEND, change_addr, FEE_RATE)
    msg, sig = sign_keypath(tx, utxo, d0, secrets.token_bytes(32))
    hexstr = finalize(tx, sig)
    print("자체 검증")
    self_check(hexstr, utxo, Q, msg, sig)
    print("testmempoolaccept:", rpc.testmempoolaccept([hexstr]))
    print("sendrawtransaction → txid", rpc.sendrawtransaction(hexstr))
    miner.generatetoaddress(1, miner.getnewaddress())
    print("잔돈 개인키 WIF (regtest 전용):", wif(dc, version=0xef))


if __name__ == "__main__":
    node() if "--node" in sys.argv else offline()
