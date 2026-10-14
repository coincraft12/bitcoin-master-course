"""3-5 실습: bech32와 bech32m — witness 버전별 규칙과 bech32의 'p 앞 q' 약점 (s35-bech32m).

실행: python part2/lesson-13/bech32m_rules.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import hashlib
import json
from lib import segwit_addr
from lib.segwit_addr import Encoding, bech32_encode, bech32_decode, convertbits

ROOT = pathlib.Path(__file__).resolve().parents[2]

# 1) 규칙: v0 → bech32, v1+ → bech32m
prog32 = bytes(range(32))
print("v0 + 32B (bech32) :", segwit_addr.encode("bc", 0, prog32))
print("v1 + 32B (bech32m):", segwit_addr.encode("bc", 1, prog32))
wrong = bech32_encode("bc", [1] + convertbits(prog32, 8, 5), Encoding.BECH32)
print("v1을 bech32로 적으면:", wrong, "→ decode", segwit_addr.decode("bc", wrong))

# 2) BIP350 무효 주소 벡터 중 '체크섬 알고리즘 오류' 네 개
V = json.load(open(ROOT / "data" / "bech32_vectors.json"))
for a in V["INVALID_ADDRESS"][1:6]:
    print("무효 벡터:", a, "→", segwit_addr.decode(a[:2].lower(), a))

# 3) bech32의 약점: 마지막 글자가 p이면 그 앞에 q를 넣어도 체크섬이 통과하는 경우
for i in range(1000):
    prog = hashlib.sha256(i.to_bytes(4, "big")).digest()[:20]
    s = bech32_encode("bc", [0] + convertbits(prog, 8, 5), Encoding.BECH32)
    if s.endswith("p"):
        break
ins = s[:-1] + "q" + s[-1]
print("\n마지막 글자가 p인 bech32  :", s)
print("p 앞에 q 삽입             :", ins)
print("체크섬만 보면              :", bech32_decode(ins)[2])
print("segwit 규칙(v0 길이)으로는 :", segwit_addr.decode("bc", ins))
s_m = bech32_encode("bc", [1] + convertbits(prog32, 8, 5), Encoding.BECH32M)
ins_m = s_m[:-1] + "q" + s_m[-1]
print("bech32m에 같은 삽입        :", bech32_decode(ins_m)[2])
