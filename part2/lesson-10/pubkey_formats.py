"""3-2 실습: 세 가지 공개키 형식과 parse_pubkey로 y 복원 (s32-code).

실행: python part2/lesson-10/pubkey_formats.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G
from lib.keys import (new_private_key, public_key, ser_uncompressed, ser_compressed,
                      ser_xonly, parse_pubkey)

# 1) 개인키 1(= G)의 세 형식 — 결정적인 값
print("[개인키 1]")
print("비압축 65B:", ser_uncompressed(G).hex())
print("압축   33B:", ser_compressed(G).hex())
print("x-only 32B:", ser_xonly(G).hex())

# 2) 새 키의 세 형식 길이와 왕복
d = new_private_key()
Q = public_key(d)
print("\n[새 키]")
for name, f in (("비압축", ser_uncompressed), ("압축", ser_compressed), ("x-only", ser_xonly)):
    print(f"{name:6}: {len(f(Q))}바이트 {f(Q).hex()}")
print("parse_pubkey(ser_compressed(Q)) == Q :", parse_pubkey(ser_compressed(Q)) == Q)
print("parse_pubkey(ser_uncompressed(Q)) == Q:", parse_pubkey(ser_uncompressed(Q)) == Q)

# 3) x좌표를 1씩 바꿔 넣어 보기 — 대략 절반은 '곡선 위의 점이 아님'
trials, fails = 40, 0
b = bytearray(ser_compressed(Q))
for _ in range(trials):
    x = (int.from_bytes(b[1:], "big") + 1).to_bytes(32, "big")
    b[1:] = x
    try:
        parse_pubkey(bytes(b))
    except ValueError:
        fails += 1
print(f"\nx+1을 {trials}번 반복: 곡선 밖 {fails}번, 곡선 위 {trials - fails}번")
