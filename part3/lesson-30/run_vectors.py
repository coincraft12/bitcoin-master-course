"""7-3 LAB (s73-code2): BIP340 공식 테스트 벡터 19개로 lib/schnorr.py 검증.

data/bip340_test_vectors.csv 열: index, secret key, public key, aux_rand, message, signature, verification result, comment
행마다 verify, 비밀키가 있는 행은 sign 결과도 대조 → PASS. FAIL이면 그 행의 comment를 읽고 빠진 검사를 찾는다.
실행: python part3/lesson-30/run_vectors.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import csv
from lib.schnorr import sign, verify

ROOT = pathlib.Path(__file__).resolve().parents[2]
passed = 0
for row in csv.DictReader(open(ROOT / "data" / "bip340_test_vectors.csv")):   # 슬라이드는 "data/…" 상대 경로 (ERRATA s73-code2)
    pub, msg, sig = (bytes.fromhex(row[c]) for c in ("public key", "message", "signature"))
    ok = verify(msg, pub, sig) == (row["verification result"] == "TRUE")
    if row["secret key"]:
        ok = ok and sign(msg, bytes.fromhex(row["secret key"]), bytes.fromhex(row["aux_rand"])) == sig
    passed += ok
    print(f"{row['index']:>2} {'PASS' if ok else 'FAIL'} {row['verification result']:<5} {row['comment']}")
print(f"{passed}/19 PASS")
