"""11-2 실습: 보조금 계산 (s112-lab). 노드 없이 실행.

    python part4/lesson-45/subsidy.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.block import COIN, subsidy, total_supply

print(subsidy(840_000) / COIN)   # 3.125
print(total_supply() / COIN)     # 20999999.9769

# (저장소 보탬) 반감기 연표, 절사, 마지막 sat, regtest 150블록 반감
print("== 반감기 연표 (s112-timeline) ==")
for i, h in enumerate(range(0, 1_050_001, 210_000)):
    print(f"{i}차  높이 {h:>9,}  보조금 {subsidy(h):>13,} sat")
print("== 2,100만이 아닌 이유 (s112-supply) ==")
print(f"정수 계산 총 발행량 {total_supply():,} sat")
print(f"등비급수(절사 없음)  {50 * COIN * 210_000 * 2:,} sat")
print(f"차이                 {50 * COIN * 210_000 * 2 - total_supply():,} sat")
first_zero = next(h for h in range(0, 64 * 210_000, 210_000) if subsidy(h) == 0)
print(f"보조금이 0이 되는 첫 높이 {first_zero:,} ({first_zero // 210_000}번째 반감기) · 직전 높이 보조금 {subsidy(first_zero - 1)} sat")
print("== regtest (nSubsidyHalvingInterval = 150) ==")
for h in (149, 150, 299, 300):
    print(f"{h}: {subsidy(h, 150)}")
