"""6-4 LAB ③ (s64-lab2): 내부키 P로 출력키 Q와 P2TR 주소를 직접 계산해 지갑과 대조.

    python part3/lesson-26/match_wallet.py                       # BIP86 공식 벡터 m/86'/0'/0'/0/0 (mainnet)
    python part3/lesson-26/match_wallet.py <desc에서 꺼낸 64자리>    # regtest 지갑 값 → Q는 witness_program, 주소는 $TR과 같아야
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.taproot import output_key, tagged_hash, tweak_pubkey
from lib import segwit_addr

if len(sys.argv) > 1:
    P_x = bytes.fromhex(sys.argv[1])
    hrp = "bcrt"
else:
    P_x = bytes.fromhex("cc8a4bc64d897bddc5fbc2f670f7a8ba0b386779106cf1223c6fc5d7cd6fc115")   # BIP86 벡터 내부키
    hrp = "bc"
Q = output_key(P_x)
print(Q.hex())                              # witness_program과 같아야
print(segwit_addr.encode(hrp, 1, Q))        # $TR과 같아야
print("t =", tagged_hash("TapTweak", P_x).hex(), "· 출력키 y 패리티", tweak_pubkey(P_x)[0])
