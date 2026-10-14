"""7-4 LAB ③ (s74-lab3): sighash 범위 체감 — DEFAULT는 출력을 고정하고, NONE은 백지수표.

    python part3/lesson-31/scope.py            # ./tr1_spend.hex + ./prevouts.json
    python part3/lesson-31/scope.py --demo     # 노드 없이: data/demo_txs.json의 P2TR 지출
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.tx import parse_tx
from lib.sighash import taproot_sighash

if "--demo" in sys.argv:
    demo = json.load(open(pathlib.Path(__file__).resolve().parents[2] / "data" / "demo_txs.json"))["txs"]["p2tr"]
    tx = parse_tx(demo["hex"])
    prev = [(demo["prev"]["value_sat"], bytes.fromhex(demo["prev"]["scriptPubKey"]))]
else:
    tx = parse_tx(open("tr1_spend.hex").read().strip())
    prev = [(round(p["amount"] * 1e8), bytes.fromhex(p["scriptPubKey"]["hex"]))
            for p in json.load(open("prevouts.json"))]

m_default = taproot_sighash(tx, prev, 0, 0x00)
m_none    = taproot_sighash(tx, prev, 0, 0x02)
tx["vout"][0]["value_sat"] += 1_000_000           # 출력 금액 변조
print(taproot_sighash(tx, prev, 0, 0x00) == m_default)   # False: DEFAULT는 출력을 고정
print(taproot_sighash(tx, prev, 0, 0x02) == m_none)      # True: NONE은 백지수표
