"""11-5 블록 헤더 version 읽기 (10-1 parse_header). regtest 노드 필요.

    python part4/lesson-48/header_versions.py 143 144 287 288 431 432
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.rpc import RPC
from lib.block import parse_header, signals_bit

rpc = RPC()
for h in map(int, sys.argv[1:]):
    raw = bytes.fromhex(rpc.getblockheader(rpc.getblockhash(h), False))
    v = parse_header(raw)["version"]
    print(f"{h:>4}: {v:#010x}  bit28={signals_bit(v, 28)}")
