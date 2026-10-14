"""2부 미니 과제 01: 테스트 니모닉으로 BIP84·BIP86 첫 주소 3개씩 계산 (s45-assign).

빈 함수 세 개를 채운다. 정답은 solution/solution_recovery_kit.py.
실제 자금의 니모닉은 절대 쓰거나 제출하지 않는다.

    python part2/lesson-18/assignment/exercise_recovery_kit.py "<테스트 니모닉>"
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.ec import G, point_mul                       # noqa: F401  (풀이에 쓴다)
from lib.keys import ser_compressed, p2wpkh_address, p2tr_address   # noqa: F401
from lib.bip39 import is_valid, mnemonic_to_seed      # noqa: F401
from lib.bip32 import master, serialize, derive_priv  # noqa: F401
from lib.taproot import output_key                    # noqa: F401


def bip84_addresses(mnemonic: str, n: int = 3, regtest: bool = True) -> list:
    """m/84h/{1h|0h}/0h/0/i (i=0..n-1)의 P2WPKH 주소. regtest면 coin_type 1h, hrp bcrt."""
    raise NotImplementedError("과제: derive_priv → 압축 공개키 → p2wpkh_address")


def bip86_addresses(mnemonic: str, n: int = 3, regtest: bool = True) -> list:
    """m/86h/{1h|0h}/0h/0/i의 P2TR 주소. 내부키 x-only → output_key → p2tr_address."""
    raise NotImplementedError("과제: 내부키 32바이트를 output_key로 조정한 뒤 bech32m으로")


def core_descriptors(mnemonic: str, purpose: int) -> tuple:
    """Core에 가져올 (받는용, 잔돈용) 디스크립터 — 체크섬 없이. 예: wpkh(tprv…/84h/1h/0h/0/*)"""
    raise NotImplementedError("과제: 마스터 tprv를 serialize(testnet=True)로 만들고 함수와 경로를 붙인다")


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "abandon " * 11 + "about"
    if not is_valid(m):
        sys.exit("니모닉 체크섬이 맞지 않습니다.")
    print("BIP84:", *bip84_addresses(m), sep="\n  ")
    print("BIP86:", *bip86_addresses(m), sep="\n  ")
    for p in (84, 86):
        r, c = core_descriptors(m, p)
        print(f"RECV{p}=\"{r}\"\nCHG{p}=\"{c}\"")
