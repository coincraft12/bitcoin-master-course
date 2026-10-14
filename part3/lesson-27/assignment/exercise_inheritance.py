"""6강 미니 과제 01·02: 상속형 Taproot 지갑 디스크립터 (s6-assign).

빈 함수 세 개를 채운다. 정답은 solution/solution_inheritance.py.
키는 자리표시(공개 테스트 니모닉)로 구조만 잡는다. MuSig2 집계키는 7-4에서 직접 만든다.

    python part3/lesson-27/assignment/exercise_inheritance.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "solution"))
from lib.ec import G, point_mul
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import taproot_tree, tweak_pubkey      # noqa: F401  (풀이에 쓴다)
from lib.keys import p2tr_address                        # noqa: F401
from descriptors import descsum_create                   # noqa: F401  (Core의 BIP380 체크섬)

BLOCKS = 52_560


def xonly(path):
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    return point_mul(G, derive_priv(seed, path)[0])[0].to_bytes(32, "big")


def leaf_script(recovery: bytes, blocks: int) -> bytes:
    """and_v(v:pk(R),older(n))를 tapscript 바이트로: <R> OP_CHECKSIGVERIFY <n> OP_CHECKSEQUENCEVERIFY"""
    raise NotImplementedError("과제: 0x20 R 0xad <스크립트 숫자 n> 0xb2 (n은 최소 바이트 리틀 엔디안, 부호 비트 주의)")


def descriptor(internal: bytes, recovery: bytes, blocks: int) -> str:
    """tr(내부키,and_v(v:pk(복구키),older(n)))#체크섬"""
    raise NotImplementedError("과제: 문자열을 만들고 descsum_create로 체크섬을 붙인다")


def address(internal: bytes, recovery: bytes, blocks: int, hrp="bcrt") -> str:
    """리프 하나짜리 트리 → 머클 루트 → 출력키 → bech32m"""
    raise NotImplementedError("과제: taproot_tree → tweak_pubkey → p2tr_address")


if __name__ == "__main__":
    agg, rec = xonly("m/86h/1h/0h/0/0"), xonly("m/86h/1h/1h/0/0")
    print("리프 스크립트:", leaf_script(rec, BLOCKS).hex())
    print("디스크립터:", descriptor(agg, rec, BLOCKS))
    print("주소:", address(agg, rec, BLOCKS))
