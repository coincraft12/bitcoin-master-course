"""3-1 실습: lib/ec.py와 lib/keys.py 확인 (s31-code3).

실행: python part2/lesson-09/ec_check.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import N, G, is_on_curve, point_add, point_mul
from lib.keys import new_private_key, public_key

# 확인: 네 줄 모두 True여야 한다. 하나라도 다르면 상수를 잘못 붙였을 가능성이 가장 크다.
print("is_on_curve(G)               :", is_on_curve(G))
print("point_mul(G, N) is None      :", point_mul(G, N) is None)
print("point_mul(G, 2) == G + G     :", point_mul(G, 2) == point_add(G, G))
print("public_key(1) == G           :", public_key(1) == G)

d = new_private_key()
Q = public_key(d)
print("개인키 d :", hex(d))
print("공개키 Q :", hex(Q[0]), hex(Q[1]))
print("Q가 곡선 위에 있는가:", is_on_curve(Q))
