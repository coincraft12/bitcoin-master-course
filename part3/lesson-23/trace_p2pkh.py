"""6-1 LAB (s61-code3 "실행"): P2PKH 송금의 scriptSig와 이전 출력 scriptPubKey를 간이 실행기에 넣어 추적.

    python part3/lesson-23/trace_p2pkh.py                                  # 노드 없이: data/demo_txs.json의 P2PKH 지출
    python part3/lesson-23/trace_p2pkh.py data/T-03/spend_legacy.hex       # 3-5 T-03 레거시 지출 (regtest 노드에서 이전 출력 조회)
checksig는 아직 기본값(항상 참)이다. 진짜 서명 검증은 7강(lesson-31 checksig_p2pkh.py)에서 연결한다.
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.script import parse_script, run
from lib.tx import parse_tx

ROOT = pathlib.Path(__file__).resolve().parents[2]

if len(sys.argv) > 1:
    from lib.rpc import RPC
    spend = parse_tx(open(sys.argv[1], encoding="utf-8").read().strip())
    vin = spend["vin"][0]
    prev = RPC().getrawtransaction(vin["txid"], True)          # txindex=1 (env/bitcoin.conf)
    script_pubkey = bytes.fromhex(prev["vout"][vin["vout"]]["scriptPubKey"]["hex"])
else:
    demo = json.load(open(ROOT / "data" / "demo_txs.json", encoding="utf-8"))["txs"]["p2pkh"]
    spend = parse_tx(demo["hex"])
    vin = spend["vin"][0]
    script_pubkey = bytes.fromhex(demo["prev"]["scriptPubKey"])
script_sig = bytes.fromhex(vin["scriptSig"])

print("scriptSig    :", [x.hex()[:16] + "…" if isinstance(x, bytes) else x for x in parse_script(script_sig)])
print("scriptPubKey :", [x.hex() if isinstance(x, bytes) else x for x in parse_script(script_pubkey)])
print("\n-- 추적 (스택은 오른쪽이 맨 위, 각 값 앞 8자리) --")
print("결과:", run(script_sig, script_pubkey))

print("\n-- 실패 실험: 공개키해시 한 바이트 바꾸기 --")
bad = bytearray(script_pubkey); bad[3] ^= 0x01
print("결과:", run(script_sig, bytes(bad)))

print("\n-- 2010년 버그 재현 시도: 해제 스크립트에 <01> OP_RETURN (OP_1 대신 1바이트 push) --")
print("결과:", run(bytes([0x01, 0x01, 0x6a]), script_pubkey))
