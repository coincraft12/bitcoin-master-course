"""4-3 실습: 같은 시드, 네 가지 주소 (s43-code).

공개된 테스트 니모닉 · 실제 자금에 절대 쓰지 말 것.
실행: python part2/lesson-16/four_addresses.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, point_mul
from lib.keys import ser_compressed, p2pkh_address, p2sh_p2wpkh_address, p2wpkh_address, p2tr_address
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import output_key

seed = mnemonic_to_seed("abandon " * 11 + "about")


def pub(path):
    k, _ = derive_priv(seed, path); return ser_compressed(point_mul(G, k))


print(p2pkh_address(pub("m/44h/0h/0h/0/0")))
print(p2sh_p2wpkh_address(pub("m/49h/0h/0h/0/0")))
print(p2wpkh_address(pub("m/84h/0h/0h/0/0")))
# BIP86은 출력키 조정이 필요하다. 6-4에서 직접 작성할 lib/taproot.py를 미리 써서 대조한다.
print(p2tr_address(output_key(pub("m/86h/0h/0h/0/0")[1:])))

# 과제: 잔돈 주소와 두 번째 계정 주소 — 모두 다른 주소 (잔액 0 체크리스트 3·4번)
print("\n[과제] BIP84")
for label, path, hrp in (("첫 받는 주소   ", "m/84h/0h/0h/0/0", "bc"), ("첫 잔돈 주소   ", "m/84h/0h/0h/1/0", "bc"),
                         ("두 번째 계정   ", "m/84h/0h/1h/0/0", "bc"), ("regtest 첫 주소", "m/84h/1h/0h/0/0", "bcrt")):
    print(label, path.ljust(16), p2wpkh_address(pub(path), hrp=hrp))
