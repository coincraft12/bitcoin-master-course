"""5-2 LAB ③ (s52-verify): 내 파서와 Core의 decoderawtransaction을 다섯 항목으로 대조.

    python part3/lesson-20/verify_with_core.py                 # ./t03_segwit.hex (t03_segwit.sh가 만든 파일)
    python part3/lesson-20/verify_with_core.py data/T-02.hex   # 레거시와 비교: txid와 wtxid가 같게 나온다
regtest 노드(bitcoin-cli)가 필요하다. 노드 없이 파서만 돌려 보려면 parse_demo.py.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx

import json, subprocess
hexstr = open(sys.argv[1] if len(sys.argv) > 1 else "t03_segwit.hex").read().strip()
mine = parse_tx(hexstr)
core = json.loads(subprocess.check_output(
    ["bitcoin-cli", "-regtest", "decoderawtransaction", hexstr]))
for k_mine, k_core in [("txid", "txid"), ("wtxid", "hash"),
        ("size", "size"), ("vsize", "vsize"), ("weight", "weight")]:
    print(k_mine, mine[k_mine] == core[k_core], mine[k_mine])
