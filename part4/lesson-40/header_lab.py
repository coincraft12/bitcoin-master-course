"""10-1 실습: 헤더 직접 해석하기 (s101-lab 오른쪽 코드). regtest 노드 필요.

    python part4/lesson-40/header_lab.py

lib/block.py의 parse_header·bits_to_target·check_pow로 노드의 최신 블록 헤더를 원시 바이트로 받아
해석한다. 기대: 모두 True. 이어서 같은 코드로 제네시스 헤더도 해석한다(prev가 모두 0).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.rpc import RPC
from lib.block import parse_header, bits_to_target, check_pow

rpc = RPC()
bh = rpc.getbestblockhash()
raw = bytes.fromhex(
  rpc.getblockheader(bh, False))
hdr = parse_header(raw)
print(hdr["hash"] == bh,
      check_pow(raw),
      hex(bits_to_target(
        hdr["bits"])))
print(hdr["prev"] ==
  rpc.getblockheader(bh)
  ["previousblockhash"])
# 기대: 모두 True

# (저장소 보탬) 제네시스 헤더를 같은 코드로
g = rpc.getblockhash(0)
graw = bytes.fromhex(rpc.getblockheader(g, False))
ghdr = parse_header(graw)
print("제네시스:", ghdr["hash"] == g, check_pow(graw), ghdr["prev"] == "00" * 32)
print("최신 헤더 필드:", {k: (hex(v) if k in ("version", "bits") else v) for k, v in hdr.items()})
