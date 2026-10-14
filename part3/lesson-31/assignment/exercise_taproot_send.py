"""3부 미니 과제: 지갑 없이 Taproot 송금 완성하기 (s7-assign).

빈 함수 네 개를 채운다. 정답은 solution/solution_taproot_send.py. 힌트는 s7-hint(조정된 개인키).
먼저 노드 없이(고정 키 + 가짜 UTXO) 끝까지 통과시킨 뒤, 정답의 --node 흐름처럼 regtest로 보낸다.

    python part3/lesson-31/assignment/exercise_taproot_send.py
실제 자금에 쓰지 말 것. 키는 공개 테스트 니모닉(abandon ×11 + about)의 m/86h/1h/0h/0/0.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.ec import G, N, point_mul                                  # noqa: F401  (풀이에 쓴다)
from lib.hashes import dsha256
from lib.keys import p2tr_address, address_to_script_pubkey
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import tagged_hash, output_key                     # noqa: F401
from lib.tx import parse_tx, serialize_tx                           # noqa: F401  (03: lib/tx.py에 추가한 직렬화 함수)
from lib.sighash import taproot_sighash                             # noqa: F401
from lib import schnorr


def tweak_seckey(d0: int) -> int:
    """내부 개인키 d0 → 출력키 Q의 개인키 (6-4: p + t). 짝수 y 맞춤, 머클 루트 없이 P.x만 (BIP86)."""
    raise NotImplementedError("과제: s7-hint")


def build_unsigned_tx(utxo: dict, to_addr: str, amount: int, change_addr: str, fee_rate: int) -> dict:
    """parse_tx 모양의 dict. version 2, 입력 1개, 출력 = 보낼 금액 + 잔돈(입력 − 금액 − 수수료). 잔돈 빼먹지 말 것(5-3)."""
    raise NotImplementedError("과제: 64바이트 자리 witness로 vsize를 재서 수수료 = fee_rate × vsize")


def sign_keypath(tx: dict, utxo: dict, d0: int, aux_rand: bytes) -> tuple:
    """(서명 해시 msg, 64바이트 서명). taproot_sighash(…, hash_type=0x00) → schnorr.sign(msg, 조정된 개인키 32B, aux_rand)"""
    raise NotImplementedError("과제: lib/sighash.py → lib/schnorr.py")


def finalize(tx: dict, sig: bytes) -> str:
    """witness = [서명] 을 붙여 SegWit 형식 hex로."""
    raise NotImplementedError("과제: tx['vin'][0]['witness'] = [sig.hex()] 후 serialize_tx")


if __name__ == "__main__":
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    d0, _ = derive_priv(seed, "m/86h/1h/0h/0/0"); dc, _ = derive_priv(seed, "m/86h/1h/0h/1/0")
    Q = output_key(point_mul(G, d0)[0].to_bytes(32, "big"))
    addr = p2tr_address(Q, hrp="bcrt")
    change = p2tr_address(output_key(point_mul(G, dc)[0].to_bytes(32, "big")), hrp="bcrt")
    utxo = {"txid": dsha256(b"part3 assignment fake utxo")[::-1].hex(), "vout": 0, "value_sat": 10_000_000,
            "scriptPubKey": address_to_script_pubkey(addr).hex()}
    tx = build_unsigned_tx(utxo, "bcrt1qp7shgcwx3mpzgxjvff0d77vuhchcldzfxnktde", 5_000_000, change, 5)
    msg, sig = sign_keypath(tx, utxo, d0, b"\x00" * 32)
    hexstr = finalize(tx, sig)
    print("서명된 트랜잭션:", hexstr)
    print("Schnorr 검증:", schnorr.verify(msg, Q, sig))
    print("txid:", parse_tx(hexstr)["txid"])
    print("정답과 같으면 txid 52f3d9ca6134e26bd276da5ea3bfaab0545d9c60bf65c481acfaa7004abb0119")
