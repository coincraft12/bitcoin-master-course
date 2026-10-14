"""7-4 LAB ② (s74-lab2): 노드가 하는 Taproot 키 경로 서명 검증을 내 코드로.

    python part3/lesson-31/verify_keypath.py           # ./tr1_spend.hex + ./prevouts.json (tr1_lab.sh가 만든 파일)
    python part3/lesson-31/verify_keypath.py --demo    # 노드 없이: data/demo_txs.json의 P2TR 지출
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.tx import parse_tx
from lib.sighash import taproot_sighash
from lib.schnorr import verify

if "--demo" in sys.argv:
    demo = json.load(open(pathlib.Path(__file__).resolve().parents[2] / "data" / "demo_txs.json", encoding="utf-8"))["txs"]["p2tr"]
    tx = parse_tx(demo["hex"])
    prev = [(demo["prev"]["value_sat"], bytes.fromhex(demo["prev"]["scriptPubKey"]))]
else:
    tx = parse_tx(open("tr1_spend.hex", encoding="utf-8").read().strip())
    prev = [(round(p["amount"] * 1e8), bytes.fromhex(p["scriptPubKey"]["hex"]))
            for p in json.load(open("prevouts.json", encoding="utf-8"))]
sig = bytes.fromhex(tx["vin"][0]["witness"][0])
hash_type = sig[64] if len(sig) == 65 else 0x00
msg = taproot_sighash(tx, prev, 0, hash_type)
out_key = prev[0][1][2:]                 # 0x51 0x20 뒤 32바이트
print(verify(msg, out_key, sig[:64]))     # True

# 출력 금액 하나를 바꾸면 다시 계산한 메시지로는 False → 서명이 출력을 고정했다
tx["vout"][0]["value_sat"] += 1
print(verify(taproot_sighash(tx, prev, 0, hash_type), out_key, sig[:64]))     # False
