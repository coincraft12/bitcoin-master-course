"""8-3 대체 규칙 중 수수료 두 가지를 숫자로 확인 (노드 없이 실행, s83-idea·s83-rules).

    규칙 1  대체본 절대 수수료 > 원본(과 함께 축출되는 것들)의 수수료 합   → 채굴자 이익 보장
    규칙 2  늘어난 수수료 ≥ 대체본 vsize × 증분 릴레이 수수료              → 재전파 대역폭 비용
    (그 밖에 축출 개수 상한, Core 31~ 피레이트 다이어그램 개선 조건이 있다 — 8-5)

실행: python part4/lesson-34/rbf_rules.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from decimal import Decimal
from lib.rpc import btc_to_sat

INCREMENTAL = Decimal("0.1")      # sat/vB, Core 30~ 기본값 (s81-estimate)


def replacement_ok(old_fees: list[int], new_fee: int, new_vsize: int, incremental=INCREMENTAL) -> tuple:
    """(규칙1 통과, 규칙2 통과, 필요한 최소 수수료)"""
    total_old = sum(old_fees)
    rule1 = new_fee > total_old
    need_extra = int((incremental * new_vsize).to_integral_value(rounding="ROUND_CEILING"))
    rule2 = new_fee - total_old >= need_extra
    return rule1, rule2, total_old + max(need_extra, 1)


if __name__ == "__main__":
    # s83-idea: 입력 X 0.5 BTC → bob 0.1, 잔돈 0.399, 수수료 0.001 / 대체본 잔돈 0.3985, 수수료 0.0015
    a_in, a_bob, a_chg = btc_to_sat("0.5"), btc_to_sat("0.1"), btc_to_sat("0.399")
    b_chg = btc_to_sat("0.3985")
    fee_a, fee_b = a_in - a_bob - a_chg, a_in - a_bob - b_chg
    print(f"원본 A 수수료   {fee_a:>7} sat")
    print(f"대체본 B 수수료 {fee_b:>7} sat (잔돈이 {a_chg - b_chg} sat 줄어든 만큼)")
    vsize = 141                       # 입력 1·출력 2 P2WPKH 예 (8-4 s84-lab2의 141 vB와 같은 모양)
    r1, r2, need = replacement_ok([fee_a], fee_b, vsize)
    print(f"규칙 1 (B > A): {r1} · 규칙 2 (증가분 ≥ {vsize} vB × {INCREMENTAL} sat/vB): {r2}")
    print("== 1 sat씩 올려 다시 보내기가 막히는 이유 ==")
    for new_fee in (fee_a + 1, fee_a + 14, fee_a + 15):
        r1, r2, need = replacement_ok([fee_a], new_fee, vsize)
        print(f"대체본 수수료 {new_fee} sat → 규칙1 {r1}, 규칙2 {r2} (최소 {need} sat)")
    print("== 피닝(8-5): 원본에 거대한 저수수료 자식이 붙어 함께 축출돼야 한다면 ==")
    child_fee = 90_000 * 1            # 9만 vB × 1 sat/vB 자식 (설명용 예)
    r1, r2, need = replacement_ok([fee_a, child_fee], fee_b, vsize)
    print(f"원본+자식 {fee_a + child_fee} sat보다 커야 함 → B({fee_b} sat)는 규칙1 {r1}, 최소 {need} sat 필요")
