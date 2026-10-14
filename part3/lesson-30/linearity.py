"""7-3 s73-linear: Schnorr의 선형성 — 두 사람의 s를 더하면 P₁ + P₂에 대한 서명 하나처럼 검증된다.

※ 단순 합산은 rogue key 공격에 취약하다. 안전하게 다듬은 것이 MuSig2(7-4, BIP327). 이 코드는 원리 확인용.
고정 키·고정 논스(공개 예제) · 실제 자금에 쓰지 말 것.
실행: python part3/lesson-30/linearity.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import hashlib
from lib.ec import G, N, FIELD_P, point_add, point_mul
from lib.schnorr import verify, tagged_hash, b32, to_int

h = lambda s: to_int(hashlib.sha256(s.encode()).digest()) % N
d1, d2 = h("linearity d1"), h("linearity d2")
k1, k2 = h("linearity k1"), h("linearity k2")
P = point_add(point_mul(G, d1), point_mul(G, d2))
R = point_add(point_mul(G, k1), point_mul(G, k2))
# BIP340은 x-only라 합친 P, R의 y가 짝수여야 한다 → 홀수면 해당 쪽 비밀값 부호를 뒤집는다
if P[1] % 2: d1, d2, P = N - d1, N - d2, (P[0], (-P[1]) % FIELD_P)
if R[1] % 2: k1, k2, R = N - k1, N - k2, (R[0], (-R[1]) % FIELD_P)
msg = hashlib.sha256(b"linearity demo").digest()
e = to_int(tagged_hash("BIP0340/challenge", b32(R[0]) + b32(P[0]) + msg)) % N
s1 = (k1 + e * d1) % N            # 참여자 1의 부분 서명
s2 = (k2 + e * d2) % N            # 참여자 2의 부분 서명
sig = b32(R[0]) + b32((s1 + s2) % N)
print("합친 공개키 P₁+P₂:", b32(P[0]).hex())
print("s₁ + s₂로 만든 64B 서명:", sig.hex())
print("P₁+P₂에 대한 보통의 BIP340 검증:", verify(msg, b32(P[0]), sig))
