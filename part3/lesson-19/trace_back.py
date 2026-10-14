"""5-1 실습 ①②를 노드 없이: 블록 170 송금(T-02)을 열고, 입력을 블록 9 코인베이스까지 거슬러 올라가 수수료 계산.

5-2에서 만드는 lib/tx.py의 parse_tx를 미리 쓴다. 수수료 필드는 어디에도 없다 → 이전 출력 금액을 찾아 빼야 한다.
실행: python part3/lesson-19/trace_back.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx

ROOT = pathlib.Path(__file__).resolve().parents[2]
tx = parse_tx((ROOT / "data" / "T-02.hex").read_text(encoding="utf-8").strip())
prev = parse_tx((ROOT / "data" / "T-02_prev.hex").read_text(encoding="utf-8").strip())


def kind(spk_hex: str) -> str:
    spk = bytes.fromhex(spk_hex)
    if len(spk) in (35, 67) and spk[0] in (33, 65) and spk[-1] == 0xac:
        return "pubkey (P2PK: 공개키를 직접 잠금에)"
    return "기타"


print("① 블록 170 송금 txid", tx["txid"])
print(f"   vin {len(tx['vin'])}개")
for i in tx["vin"]:
    print(f"     txid {i['txid'][:8]}…{i['txid'][-6:]}, vout {i['vout']}")
print(f"   vout {len(tx['vout'])}개")
for n, o in enumerate(tx["vout"]):
    print(f"     {n}: {o['value_sat']:>13,} sat = {o['value_sat'] // 100_000_000} BTC · 유형 {kind(o['scriptPubKey'])}")

print("\n② 입력이 가리키는 이전 트랜잭션", prev["txid"])
cb = prev["vin"][0]
print(f"   코인베이스인가: txid가 0으로 채워짐 {cb['txid'] == '00' * 32}, vout 0x{cb['vout']:08x}")
print(f"   scriptSig(채굴자 임의 데이터) {cb['scriptSig']}")
spent = prev["vout"][tx["vin"][0]["vout"]]["value_sat"]
out_sum = sum(o["value_sat"] for o in tx["vout"])
print(f"   출력 {tx['vin'][0]['vout']}번 = {spent:,} sat")
print(f"\n수수료 = 입력 {spent:,} − 출력 {out_sum:,} = {spent - out_sum} sat")
