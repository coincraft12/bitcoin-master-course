"""11-3 실습: 코인베이스 태그로 풀 점유율 집계 (s113-lab). 메인넷 노드 필요.

    python part4/lesson-46/coinbase_tags.py            # 메인넷 최근 1,000블록 (슬라이드 그대로)
    python part4/lesson-46/coinbase_tags.py regtest    # 형식 확인용 (regtest 블록에는 태그가 없다)

메인넷 노드가 없으면 탐색기의 풀 통계 페이지와 tag_offline.py(data/coinbase_tags.json)로 진행한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import re
from collections import Counter
from lib.rpc import RPC

rpc = RPC(network="main") if len(sys.argv) < 2 else RPC(network=sys.argv[1])
tip = rpc.getblockcount()
tags = Counter()
for h in range(max(tip - 999, 1), tip + 1):        # (저장소 보완) 1,000블록이 안 되는 체인은 1부터
    blk = rpc.getblock(rpc.getblockhash(h), 2)
    cb = bytes.fromhex(blk["tx"][0]["vin"][0]["coinbase"])
    text = "".join(chr(b) if 32 <= b < 127 else " " for b in cb)
    words = [w for w in re.split(r"\s+", text) if len(w) >= 4]
    tags[words[0] if words else "(unknown)"] += 1
for tag, n in tags.most_common(10):
    print(f"{tag:<24} {n:>4}  {n / 10:.1f}%")
