"""5-2 LAB ②를 노드 없이: lib/tx.py의 parse_tx로 레거시·SegWit 트랜잭션을 바이트 단위로 읽는다.

    python part3/lesson-20/parse_demo.py                  # 저장소 예제 세 개
    python part3/lesson-20/parse_demo.py t03_segwit.hex   # 내 노드에서 받은 hex
예제: T-02(블록 170, 레거시) · demo P2WPKH 지출(data/demo_txs.json, lib으로 만든 결정적 예제) · BIP143 공식 예제(서명 후)
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx

ROOT = pathlib.Path(__file__).resolve().parents[2]


def show(name, hexstr):
    t = parse_tx(hexstr)
    print(f"== {name} ==")
    print(f"version {t['version']} · segwit {t['segwit']} · 입력 {len(t['vin'])} · 출력 {len(t['vout'])} · locktime {t['locktime']}")
    for n, i in enumerate(t["vin"]):
        w = f" · witness {len(i['witness'])}개 {[len(x) // 2 for x in i['witness']]}B" if "witness" in i else ""
        print(f"  vin[{n}] {i['txid'][:16]}…:{i['vout']} scriptSig {len(i['scriptSig']) // 2}B{w}")
    for n, o in enumerate(t["vout"]):
        print(f"  vout[{n}] {o['value_sat']:,} sat · scriptPubKey {o['scriptPubKey']}")
    base = (t["weight"] - t["size"]) // 3
    print(f"txid   {t['txid']}")
    print(f"wtxid  {t['wtxid']}  (txid와 같음: {t['txid'] == t['wtxid']})")
    print(f"size {t['size']} · base {base} · weight {base}×3+{t['size']} = {t['weight']} · vsize {t['vsize']}\n")


if len(sys.argv) > 1:
    show(sys.argv[1], open(sys.argv[1]).read().strip())
else:
    show("T-02 블록 170 (레거시)", (ROOT / "data" / "T-02.hex").read_text().strip())
    demo = json.load(open(ROOT / "data" / "demo_txs.json"))["txs"]["p2wpkh"]
    show("demo P2WPKH 지출 (SegWit v0)", demo["hex"])
    b143 = json.load(open(ROOT / "data" / "bip143_examples.json"))["examples"][0]
    show("BIP143 Native P2WPKH 예제 (P2PK 입력 + P2WPKH 입력)", b143["signed_tx"])
