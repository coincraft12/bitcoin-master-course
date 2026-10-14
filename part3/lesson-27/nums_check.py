"""6-5 s65-nums: BIP341 NUMS 점 H = lift_x(SHA256(G의 비압축 직렬화))를 직접 계산해 확인.

실행: python part3/lesson-27/nums_check.py
"""
import sys, pathlib, hashlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G
from lib.keys import ser_uncompressed
from lib.taproot import lift_x, NUMS_H

h = hashlib.sha256(ser_uncompressed(G)).digest()
H = lift_x(int.from_bytes(h, "big"))          # 곡선 위에 있어야 오류 없이 점이 나온다
print("SHA256(0x04‖G.x‖G.y) =", h.hex())
print("H.x                   =", H[0].to_bytes(32, "big").hex())
print("슬라이드 값과 같음     :", H[0].to_bytes(32, "big") == NUMS_H)
print("해시에서 나온 x라 누구도 H = h·G인 h를 미리 알 수 없다 → 키 경로 봉쇄")
