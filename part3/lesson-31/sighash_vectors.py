"""7-4 (s74-code2 아래 줄): 공식 벡터로 lib/sighash.py 확인.

- BIP341 wallet-test-vectors keyPathSpending: annex 없는 키 경로 입력 7개(ALL·NONE·SINGLE·ANYONECANPAY 조합)의 sigHash
- BIP143 문서 Example 절의 sigHash 13개 (s74-amount "BIP143")
- Bitcoin Core src/test/data/sighash.json 레거시 500개 (s74-amount "LEGACY")
실행: python part3/lesson-31/sighash_vectors.py
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx
from lib.sighash import taproot_sighash, bip143_sighash, legacy_sighash

DATA = pathlib.Path(__file__).resolve().parents[2] / "data"
NAMES = {0x00: "DEFAULT", 0x01: "ALL", 0x02: "NONE", 0x03: "SINGLE", 0x81: "ALL|ANYONECANPAY",
         0x82: "NONE|ANYONECANPAY", 0x83: "SINGLE|ANYONECANPAY"}

k = json.load(open(DATA / "bip341_wallet_test_vectors.json"))["keyPathSpending"][0]
tx = parse_tx(k["given"]["rawUnsignedTx"])
prev = [(u["amountSats"], bytes.fromhex(u["scriptPubKey"])) for u in k["given"]["utxosSpent"]]
print("BIP341 키 경로 sigHash")
for inp in k["inputSpending"]:
    g = inp["given"]
    got = taproot_sighash(tx, prev, g["txinIndex"], g["hashType"]).hex()
    print(f"  입력 {g['txinIndex']} {NAMES[g['hashType']]:<20} {got[:16]}… {got == inp['intermediary']['sigHash']}")

ok = 0; ex = json.load(open(DATA / "bip143_examples.json"))["examples"]
for e in ex:
    t = parse_tx(e["unsigned_tx"])
    ok += bip143_sighash(t, e["input_index"], bytes.fromhex(e["script_code"]), e["amount_sat"], e["hash_type"]).hex() == e["sighash"]
print(f"BIP143 예제 sigHash 일치 {ok}/{len(ex)}")

rows = json.load(open(DATA / "sighash.json"))[1:]
ok = sum(legacy_sighash(parse_tx(r), i, bytes.fromhex(s), h)[::-1].hex() == exp for r, s, i, h, exp in rows)
print(f"레거시 sighash.json 일치 {ok}/{len(rows)}")
