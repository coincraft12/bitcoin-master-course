"""7-1 LAB (s71-code2 아래 줄): 검증된 라이브러리와 교차 확인 — 라이브러리 서명 → 내 verify, 내 DER → 라이브러리.

coincurve(libsecp256k1 파이썬 바인딩)가 필요하다: pip install coincurve   (lib은 표준 라이브러리만 쓰고, 이 확인 스크립트만 예외)
실행: python part3/lesson-28/cross_check.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import hashlib
try:
    import coincurve
except ImportError:
    sys.exit("coincurve가 없습니다: pip install coincurve")
from lib.ec import G, point_mul
from lib.keys import ser_compressed
from lib.ecdsa import sign, verify, der, parse_der, sign_rfc6979

d = int.from_bytes(hashlib.sha256(b"lesson-28 cross check key").digest(), "big")   # 고정 예제 키 · 실제 자금 금지
Q = point_mul(G, d)
z = int.from_bytes(hashlib.sha256(b"CoinCraft").digest(), "big")
msg32 = z.to_bytes(32, "big")
sk = coincurve.PrivateKey(d.to_bytes(32, "big"))
assert sk.public_key.format() == ser_compressed(Q)

lib_sig = sk.sign(msg32, hasher=None)                  # libsecp256k1: RFC6979 논스 + low-S, DER
print("라이브러리 서명 → 내 verify :", verify(Q, z, *parse_der(lib_sig)))
mine = der(*sign(d, z))                                # 내 서명(무작위 k)
print("내 DER 서명 → 라이브러리     :", coincurve.PublicKey(ser_compressed(Q)).verify(mine, msg32, hasher=None))
print("RFC6979 서명 바이트 일치     :", der(*sign_rfc6979(d, z)) == lib_sig)
print("libsecp256k1 DER:", lib_sig.hex())
