"""4-2 실습: 개인키 쪽 파생과 공개키 쪽 파생이 같은 점을 주는가 (s42-watch, s42-code2).

실행: python part2/lesson-15/ckd_pub_check.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, point_mul
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import HARD, ckd_priv, ckd_pub, derive_priv

seed = mnemonic_to_seed("abandon " * 11 + "about")          # 공개된 테스트 니모닉
k, c = derive_priv(seed, "m/84h/1h/0h")
K = point_mul(G, k)
for i in range(5):
    kc, _ = ckd_priv(k, c, i)
    Kc, _ = ckd_pub(K, c, i)
    print(f"자식 {i}: ckd_priv의 공개키 == ckd_pub 결과 → {point_mul(G, kc) == Kc}")
try:
    ckd_pub(K, c, HARD + 5)
except ValueError as e:
    print("강화 번호 5h로 ckd_pub:", e)
