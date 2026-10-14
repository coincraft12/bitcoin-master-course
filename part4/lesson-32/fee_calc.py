"""8-1 수수료 계산 (노드 없이 실행).

    수수료(sat) = 수수료율(sat/vB) × vsize(vB)

실행:
    python part4/lesson-32/fee_calc.py                     # 슬라이드 예제
    python part4/lesson-32/fee_calc.py 141 5               # vsize 141 vB, 5 sat/vB
    python part4/lesson-32/fee_calc.py --check '{"fee": -0.00000705, "vsize": 141}' 5
        → fee_lab.sh 3단계의 jq 출력({fee, vsize})이 정말 5 × vsize sat인지 확인

금액은 sat 정수. 수수료율에 소수(0.1 sat/vB 등)가 올 수 있어 Decimal로 받고, 결과는 Core처럼 올림한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from decimal import Decimal, ROUND_CEILING
from lib.rpc import btc_to_sat


def fee_sat(vsize: int, sat_per_vb) -> int:
    """수수료율 × vsize를 sat 정수로 (소수점은 올림)."""
    return int((Decimal(str(sat_per_vb)) * vsize).to_integral_value(rounding=ROUND_CEILING))


def feerate(fee_sat_: int, vsize: int) -> Decimal:
    """실효 수수료율(sat/vB), 소수 둘째 자리까지."""
    return (Decimal(fee_sat_) / vsize).quantize(Decimal("0.01"))


def check(jq_out: str, rate) -> bool:
    """gettransaction의 {fee, vsize} → fee(BTC, 음수)를 sat로 바꿔 rate × vsize와 비교."""
    d = json.loads(jq_out, parse_float=Decimal)
    paid = -btc_to_sat(d["fee"])
    want = fee_sat(d["vsize"], rate)
    print(f"낸 수수료 {paid} sat · {rate} × {d['vsize']} vB = {want} sat → {'일치' if paid == want else '불일치'}"
          f" (실효 {feerate(paid, d['vsize'])} sat/vB)")
    return paid == want


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--check":
        sys.exit(0 if check(sys.argv[2], sys.argv[3]) else 1)
    if len(sys.argv) == 3:
        v, r = int(sys.argv[1]), sys.argv[2]
        print(f"{v} vB × {r} sat/vB = {fee_sat(v, r)} sat")
        sys.exit(0)
    print("== 8-1 퀴즈 Q1: vsize 150 vB, 20 sat/vB ==")
    print(f"150 × 20 = {fee_sat(150, 20)} sat")
    print("== 금액과 무관: 같은 vsize면 100 BTC를 보내든 0.001 BTC를 보내든 같다 ==")
    for amount in ("100", "0.001"):
        print(f"보내는 금액 {amount:>5} BTC, 141 vB, 5 sat/vB → {fee_sat(141, 5)} sat")
    print("== 최소 릴레이 수수료 (Core 30~ 기본 0.1 sat/vB, 이전 1 sat/vB) ==")
    for r in ("0.1", "1"):
        print(f"141 vB × {r} sat/vB = {fee_sat(141, r)} sat")
