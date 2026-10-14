"""7-2 LAB (s72-code): 같은 k로 만든 서명 두 개에서 개인키 복원 → RFC6979로 재실험.

    python part3/lesson-29/nonce_reuse.py            # 결정적: 고정 개인키·고정 k (README 기대 출력과 같다)
    python part3/lesson-29/nonce_reuse.py --random   # 슬라이드 그대로 secrets로 d·k를 뽑는다 (값은 매번 다르고 결과는 True)
교육용 데모 · 공개된 고정 키 · 실제 자금에 쓰지 말 것.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import hashlib, secrets
from lib.ec import G, N, point_mul
from lib.ecdsa import sign, sign_rfc6979

RANDOM = "--random" in sys.argv
if RANDOM:
    d = secrets.randbelow(N - 1) + 1; Q = point_mul(G, d)
else:
    d = int.from_bytes(hashlib.sha256(b"lesson-29 victim key").digest(), "big") % N; Q = point_mul(G, d)
h = lambda m: int.from_bytes(hashlib.sha256(m).digest(), "big")
z1, z2 = h(b"pay Alice 1 BTC"), h(b"pay Bob 2 BTC")
if RANDOM:
    k = secrets.randbelow(N - 1) + 1          # 실수: 같은 k를 두 번
else:
    k = int.from_bytes(hashlib.sha256(b"lesson-29 reused nonce").digest(), "big") % N
r1, s1 = sign(d, z1, k); r2, s2 = sign(d, z2, k)
assert r1 == r2                           # 단서


def recover(r, s1, z1, s2, z2, Q):
    for a in (s1, N - s1):
        for b in (s2, N - s2):
            if a == b: continue
            k = (z1 - z2) * pow(a - b, -1, N) % N
            d = (a * k - z1) * pow(r, -1, N) % N
            if point_mul(G, d) == Q: return d


print("== 같은 k로 두 메시지에 서명 ==")
print("r1 == r2 (단서):", r1 == r2, f"r = {r1:064x}" if not RANDOM else "")
found = recover(r1, s1, z1, s2, z2, Q)
print(recover(r1, s1, z1, s2, z2, Q) == d)    # True
if not RANDOM:
    print("원래 개인키  :", f"{d:064x}")
    print("복원한 개인키:", f"{found:064x}")

print("\n== RFC6979 논스로 다시 ==")
a1, b1 = sign_rfc6979(d, z1); a2, b2 = sign_rfc6979(d, z2)
print("r1 == r2:", a1 == a2, "→ 단서가 없다")
print("같은 방법으로 복원 시도:", recover(a1, b1, z1, b2, z2, Q) == d)
print("같은 메시지 두 번 = 같은 서명:", sign_rfc6979(d, z1) == (a1, b1), "(안전: 두 식을 빼도 얻을 정보가 없다)")
