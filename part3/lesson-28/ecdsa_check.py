"""7-1 LAB (s71-code2 "확인"): lib/ecdsa.py 서명·검증·DER 확인.

실행: python part3/lesson-28/ecdsa_check.py
앞 네 줄은 슬라이드 그대로(무작위 키·논스라 DER 길이는 실행마다 70 또는 71). 뒤는 고정 키로 DER 구조를 뜯어 본다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import hashlib, secrets
from lib.ec import G, N, point_mul
from lib.ecdsa import sign, verify, der, parse_der, sign_rfc6979

# 확인 (슬라이드 그대로)
d = secrets.randbelow(N - 1) + 1; Q = point_mul(G, d)
z = int.from_bytes(hashlib.sha256(b"CoinCraft").digest(), "big")
r, s = sign(d, z)
print(verify(Q, z, r, s))        # True
print(verify(Q, z + 1, r, s))    # False: 메시지 변조
print(verify(Q, z, r, N - s))    # True: high-S도 수학적으로는 유효
print(len(der(r, s)))            # 70~71 (+ sighash 1B) — ERRATA s71-code2

# 고정 키(개인키 1, 공개 예제 · 실제 자금 금지)로 DER 구조 보기 — RFC6979라 결정적
d1 = 1
r, s = sign_rfc6979(d1, z)
sig = der(r, s)
print("\nDER", len(sig), "B:", sig.hex())
i = 4 + sig[3]
print(f"  30 {sig[1]:02x} | 02 {sig[3]:02x} r={sig[4:i].hex()} | 02 {sig[i+1]:02x} s={sig[i+2:].hex()}")
print("  r의 최상위 비트가 1 → 앞에 0x00:", r >> 255 == 1, "· low-S(s ≤ n/2):", s <= N // 2)
print("  parse_der 왕복:", parse_der(sig) == (r, s))
print("  high-S(n − s)로 바꾼 DER 길이:", len(der(r, N - s)), "· n − s의 최상위 비트:", (N - s) >> 255)
