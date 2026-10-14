"""3-4 실습: Core bech32 주소와 내 계산 대조.

    python part2/lesson-12/check_core_bech32.py <pubkey hex> <bcrt1q… 주소> <witness_program hex>
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.hashes import hash160
from lib.keys import p2wpkh_address, p2sh_p2wpkh_address

if len(sys.argv) != 4:
    sys.exit("사용법: python part2/lesson-12/check_core_bech32.py <pubkey> <주소> <witness_program>")
pub, core_addr, prog = bytes.fromhex(sys.argv[1]), sys.argv[2], sys.argv[3]
print("p2wpkh_address(hrp=bcrt) :", p2wpkh_address(pub, hrp="bcrt"))
print("Core 주소                :", core_addr)
print("주소 일치                :", p2wpkh_address(pub, hrp="bcrt") == core_addr)
print("hash160 == program       :", hash160(pub).hex() == prog)
print("hrp=bc로 잘못 계산하면   :", p2wpkh_address(pub))
print("p2sh_p2wpkh(0xc4)        :", p2sh_p2wpkh_address(pub, 0xc4))
