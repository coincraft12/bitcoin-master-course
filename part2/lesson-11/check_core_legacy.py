"""3-3 실습 4단계: Core legacy 주소와 내 계산 대조 (regtest 버전 0x6f).

    python part2/lesson-11/check_core_legacy.py <pubkey hex> <Core 주소>
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.base58 import b58check_decode
from lib.keys import p2pkh_address

if len(sys.argv) != 3:
    sys.exit("사용법: python part2/lesson-11/check_core_legacy.py <pubkey hex> <주소>")
pub, core_addr = bytes.fromhex(sys.argv[1]), sys.argv[2]
mine = p2pkh_address(pub, 0x6f)
print("내 계산 :", mine)
print("Core    :", core_addr)
print("일치    :", mine == core_addr)
i = len(core_addr) // 2
typo = core_addr[:i] + ("2" if core_addr[i] != "2" else "3") + core_addr[i + 1:]
try:
    b58check_decode(typo)
    print(f"오타 {typo}: 통과 (극히 드문 경우)")
except ValueError as e:
    print(f"오타 {typo}: {e}")
print(typo)
