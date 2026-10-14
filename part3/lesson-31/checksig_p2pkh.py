"""7-4 → 6-1 연결: 간이 실행기 run()의 checksig 자리에 진짜 검증(서명 해시 + ECDSA)을 넣는다 (s71-code2 "6-1 실행기 checksig에 연결").

    python part3/lesson-31/checksig_p2pkh.py
① 저장소 demo P2PKH 지출 (lib으로 만든 결정적 예제) ② 블록 170 송금 T-02(P2PK, 2009년 사토시의 서명)
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx
from lib.script import run
from lib.sighash import legacy_sighash
from lib.ecdsa import verify, parse_der
from lib.keys import parse_pubkey

DATA = pathlib.Path(__file__).resolve().parents[2] / "data"


def make_checksig(tx, idx, script_code):
    def checksig(sig: bytes, pub: bytes) -> bool:
        z = int.from_bytes(legacy_sighash(tx, idx, script_code, sig[-1]), "big")   # 마지막 1바이트 = sighash 유형
        r, s = parse_der(sig[:-1])
        return verify(parse_pubkey(pub), z, r, s)
    return checksig


demo = json.load(open(DATA / "demo_txs.json", encoding="utf-8"))["txs"]["p2pkh"]
tx = parse_tx(demo["hex"]); spk = bytes.fromhex(demo["prev"]["scriptPubKey"])
print("== ① demo P2PKH: 진짜 checksig ==")
print("결과:", run(bytes.fromhex(tx["vin"][0]["scriptSig"]), spk, checksig=make_checksig(tx, 0, spk)))
tx["vout"][0]["value_sat"] -= 1                       # 서명 뒤에 금액을 바꾸면
print("출력 금액 1 sat 변조 후:", run(bytes.fromhex(tx["vin"][0]["scriptSig"]), spk,
                                   checksig=make_checksig(tx, 0, spk), trace=False))

t02 = parse_tx((DATA / "T-02.hex").read_text(encoding="utf-8").strip())
prev = parse_tx((DATA / "T-02_prev.hex").read_text(encoding="utf-8").strip())
spk = bytes.fromhex(prev["vout"][t02["vin"][0]["vout"]]["scriptPubKey"])     # P2PK: <공개키 65B> OP_CHECKSIG
print("\n== ② 블록 170 (P2PK) ==")
print("결과:", run(bytes.fromhex(t02["vin"][0]["scriptSig"]), spk, checksig=make_checksig(t02, 0, spk)))
