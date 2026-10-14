# part1/lesson-08/recent_blocks.py
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib.rpc import RPC
rpc = RPC()
tip = rpc.getblockcount()
print(f"{'height':>6} {'nTx':>4} {'size':>7} {'weight':>8}  hash")
for h in range(max(0, tip - 9), tip + 1):
    b = rpc.getblock(rpc.getblockhash(h), 1)
    print(f"{b['height']:>6} {b['nTx']:>4} {b['size']:>7} {b['weight']:>8}  {b['hash'][:16]}…")
alice = RPC(wallet="alice")
print("alice:", alice.getbalance(), "BTC =", int(alice.getbalance() * 100_000_000), "sat")
