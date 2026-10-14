"""11-1 실습: 비트 수를 늘리며 측정하기 (s111-lab2). regtest 노드 필요.

    python part4/lesson-44/mine_lab.py

regtest 최신 블록 헤더의 앞 76바이트에 nonce를 붙여 상위 k비트가 0인 해시를 찾는다.
노드 없이 같은 실험을 하려면 mine_genesis.py.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.rpc import RPC
from lib.block import mine

rpc = RPC()
prefix = bytes.fromhex(rpc.getblockheader(
    rpc.getbestblockhash(), False))[:76]
for k in (8, 12, 16, 20):
    nonce, h, sec = mine(prefix, k)
    print(f"{k:>2}비트 nonce={nonce:>9} {sec:6.2f}s")
