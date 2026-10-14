"""data/demo_txs.json 생성기 — 노드 없이 쓰는 결정적 예제 트랜잭션 세 개 (3부).

교육용 · 가짜 UTXO · 실제 자금에 쓰지 말 것.

공개된 테스트 니모닉(abandon ×11 + about, 패스프레이즈 없음)의 regtest 경로 키로
P2PKH · P2WPKH · P2TR 입력 하나씩을 지출하는 트랜잭션을 lib만으로 만들고 서명한다.
- 이전 출력(UTXO)은 가짜다: txid = SHA256d("bmc demo utxo <유형>"), vout 0, 0.1 BTC.
- 출력 구성은 셋 다 같다: bob(P2WPKH) 0.09 BTC + 잔돈(P2WPKH), 수수료율 5 sat/vB (3-5 measure_sizes.sh와 같은 구성).
- 수수료 = 5 sat/vB × vsize 이상 (ECDSA 서명 길이가 ±1B 흔들려 1 vB만큼 더 낼 수 있다).
- ECDSA는 RFC6979 결정적 논스, Schnorr는 aux_rand = 0x00×32라서 몇 번 실행해도 같은 바이트가 나온다.

쓰는 곳: 5강 미니 과제 정답의 노드 없는 비교표, 6-1 P2PKH 실행 추적, 7-4 checksig 연결.
실행: python data/make_demo_txs.py   (결과를 data/demo_txs.json에 덮어쓴다. tests/test_tx.py가 재생성 결과와 파일이 같은지 확인)
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.ec import G, N, point_mul
from lib.hashes import hash160, dsha256
from lib.keys import ser_compressed, p2pkh_address, p2wpkh_address, p2tr_address, address_to_script_pubkey
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import tagged_hash, output_key
from lib.tx import parse_tx, serialize_tx
from lib.sighash import legacy_sighash, bip143_sighash, taproot_sighash, p2wpkh_script_code
from lib import ecdsa, schnorr

SEED = mnemonic_to_seed("abandon " * 11 + "about")
FEE_RATE = 5                    # sat/vB
IN_VALUE = 10_000_000           # 0.1 BTC
TO_BOB = 9_000_000              # 0.09 BTC


def key(path):
    d, _ = derive_priv(SEED, path)
    return d, ser_compressed(point_mul(G, d))


def push(b: bytes) -> bytes:
    assert len(b) <= 0x4b
    return bytes([len(b)]) + b


def tweak_seckey(d0: int) -> int:
    P = point_mul(G, d0)
    d = d0 if P[1] % 2 == 0 else N - d0
    t = int.from_bytes(tagged_hash("TapTweak", P[0].to_bytes(32, "big")), "big")
    return (d + t) % N


BOB = p2wpkh_address(key("m/84h/1h/1h/0/0")[1], hrp="bcrt")       # 두 번째 계정을 bob으로
CHANGE = p2wpkh_address(key("m/84h/1h/0h/1/0")[1], hrp="bcrt")    # 잔돈 체인 /1/

PATHS = {"p2pkh": "m/44h/1h/0h/0/0", "p2wpkh": "m/84h/1h/0h/0/0", "p2tr": "m/86h/1h/0h/0/0"}


def address_of(kind, pub):
    if kind == "p2pkh": return p2pkh_address(pub, version=0x6f)
    if kind == "p2wpkh": return p2wpkh_address(pub, hrp="bcrt")
    return p2tr_address(output_key(pub[1:]), hrp="bcrt")


def build(kind: str, fee: int) -> dict:
    d, pub = key(PATHS[kind])
    addr = address_of(kind, pub)
    spk = address_to_script_pubkey(addr)
    prev_txid = dsha256(f"bmc demo utxo {kind}".encode())[::-1].hex()
    tx = {"version": 2, "locktime": 0,
          "vin": [{"txid": prev_txid, "vout": 0, "scriptSig": "", "sequence": 0xfffffffd}],
          "vout": [{"value_sat": TO_BOB, "scriptPubKey": address_to_script_pubkey(BOB).hex()},
                   {"value_sat": IN_VALUE - TO_BOB - fee, "scriptPubKey": address_to_script_pubkey(CHANGE).hex()}]}
    if kind == "p2pkh":
        z = int.from_bytes(legacy_sighash(tx, 0, spk, 0x01), "big")
        sig = ecdsa.der(*ecdsa.sign_rfc6979(d, z)) + b"\x01"
        tx["vin"][0]["scriptSig"] = (push(sig) + push(pub)).hex()
    elif kind == "p2wpkh":
        z = int.from_bytes(bip143_sighash(tx, 0, p2wpkh_script_code(hash160(pub)), IN_VALUE, 0x01), "big")
        sig = ecdsa.der(*ecdsa.sign_rfc6979(d, z)) + b"\x01"
        tx["vin"][0]["witness"] = [sig.hex(), pub.hex()]
    else:
        msg = taproot_sighash(tx, [(IN_VALUE, spk)], 0, 0x00)
        sig = schnorr.sign(msg, tweak_seckey(d).to_bytes(32, "big"), b"\x00" * 32)
        tx["vin"][0]["witness"] = [sig.hex()]
    raw = serialize_tx(tx).hex()
    p = parse_tx(raw)
    return {"path": PATHS[kind], "address": addr,
            "prev": {"txid": prev_txid, "vout": 0, "value_sat": IN_VALUE, "scriptPubKey": spk.hex()},
            "hex": raw, "txid": p["txid"], "wtxid": p["wtxid"], "size": p["size"], "weight": p["weight"],
            "vsize": p["vsize"], "fee_sat": fee}


def make() -> dict:
    txs = {}
    for kind in PATHS:
        fee = 0
        while True:            # 수수료가 바뀌면 서명(=DER 길이)도 바뀔 수 있어, 수수료율 이상이 될 때까지 올린다
            t = build(kind, fee)
            if t["fee_sat"] >= FEE_RATE * t["vsize"]:
                break
            fee = FEE_RATE * t["vsize"]
        txs[kind] = t
    return {"note": "lib으로 만든 결정적 예제 · 가짜 UTXO · 공개 테스트 니모닉 키 · 실제 자금에 쓰지 말 것 (data/make_demo_txs.py)",
            "mnemonic": "abandon ×11 + about (패스프레이즈 없음)", "fee_rate_sat_vb": FEE_RATE,
            "bob": BOB, "change": CHANGE, "txs": txs}


if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent / "demo_txs.json"
    out.write_text(json.dumps(make(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, t in json.loads(out.read_text(encoding="utf-8"))["txs"].items():
        print(f"{k:<7} vsize {t['vsize']:>3}  weight {t['weight']:>3}  fee {t['fee_sat']} sat  txid {t['txid']}")
    print("저장:", out)
