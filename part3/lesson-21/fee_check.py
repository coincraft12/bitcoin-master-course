"""5-3 LAB ②: 수수료 = 입력 합 − 출력 합, 수수료율 = 수수료 ÷ vsize (5-2 파서로).

    python part3/lesson-21/fee_check.py <hex 파일 또는 hex> <입력 금액 합 sat>
    python part3/lesson-21/fee_check.py                     # 저장소 demo 세 개 (노드 없이)
트랜잭션에는 수수료 칸이 없으므로 입력 금액(이전 출력 금액)은 따로 알려 줘야 한다.
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.tx import parse_tx

DUST = {"P2PKH": 546, "P2WPKH": 294, "P2TR": 330}      # s53-accident 기본 설정 더스트 기준 (미만이면 더스트)


def out_type(spk: bytes) -> str:
    if len(spk) == 25 and spk[:3] == b"\x76\xa9\x14": return "P2PKH"
    if len(spk) == 22 and spk[:2] == b"\x00\x14": return "P2WPKH"
    if len(spk) == 34 and spk[:2] == b"\x51\x20": return "P2TR"
    return "기타"


def report(name: str, hexstr: str, in_sat: int):
    t = parse_tx(hexstr)
    out_sat = sum(o["value_sat"] for o in t["vout"])
    fee = in_sat - out_sat
    print(f"== {name} ==")
    for n, o in enumerate(t["vout"]):
        ty = out_type(bytes.fromhex(o["scriptPubKey"]))
        dust = " ← 더스트!" if ty in DUST and o["value_sat"] < DUST[ty] else ""
        print(f"  출력 {n}: {o['value_sat']:>11,} sat ({ty}){dust}")
    rate100 = fee * 100 // t["vsize"]                  # 정수 연산 (소수 둘째 자리까지 버림)
    print(f"  수수료 = {in_sat:,} − {out_sat:,} = {fee:,} sat · vsize {t['vsize']} vB → {rate100 // 100}.{rate100 % 100:02d} sat/vB")
    if fee * 1000 > 10_000_000 * t["vsize"]:          # 0.10 BTC/kvB = 10,000,000 sat / 1000 vB
        print("  경고: 수수료율이 sendrawtransaction 기본 maxfeerate 0.10 BTC/kvB를 넘는다 → 전파 거부")


if len(sys.argv) == 3:
    arg = sys.argv[1]
    hexstr = open(arg, encoding="utf-8").read().strip() if pathlib.Path(arg).exists() else arg
    report(arg, hexstr, int(sys.argv[2]))
else:
    ROOT = pathlib.Path(__file__).resolve().parents[2]
    for k, t in json.load(open(ROOT / "data" / "demo_txs.json", encoding="utf-8"))["txs"].items():
        report(f"demo {k} 입력 지출", t["hex"], t["prev"]["value_sat"])
    # s53-q·LAB ① 재현: 0.3 BTC 코인으로 bob에게 0.1 BTC만 적은 경우 (demo P2WPKH 모양을 빌려 크기만 계산)
    from lib.tx import serialize_tx
    t = parse_tx(json.load(open(ROOT / "data" / "demo_txs.json", encoding="utf-8"))["txs"]["p2wpkh"]["hex"])
    t["vout"] = [dict(t["vout"][0], value_sat=10_000_000)]
    report("0.3 BTC 입력, 출력은 bob 0.1 BTC 하나 (잔돈 누락)", serialize_tx(t).hex(), 30_000_000)
