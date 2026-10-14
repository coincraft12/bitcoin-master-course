"""10-2 실습: 머클 루트 계산 (s102-lab 오른쪽 위 코드). regtest 노드, miner·alice·bob 지갑 필요.

    python part4/lesson-41/merkle_lab.py         # 송금 3건 + 블록 1개 → 트랜잭션 4개 (짝수)
    python part4/lesson-41/merkle_lab.py 2       # 송금 2건 → 트랜잭션 3개 (홀수 복제 확인)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.rpc import RPC
from lib.block import merkle_root

rpc = RPC()
alice, bob, miner = RPC(wallet="alice"), RPC(wallet="bob"), RPC(wallet="miner")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
# 송금 n건 + 블록 1개 (저장소 보탬: 슬라이드의 "송금 3건 + 블록 1개 후"를 스크립트로)
for _ in range(n):
    alice.sendtoaddress(bob.getnewaddress(), "0.01")
miner.generatetoaddress(1, miner.getnewaddress())

# 송금 3건 + 블록 1개 후
blk = rpc.getblock(
  rpc.getbestblockhash(), 1)
print(len(blk["tx"]),
  merkle_root(blk["tx"])
  == blk["merkleroot"])
# 4, True · 홀수 블록도
