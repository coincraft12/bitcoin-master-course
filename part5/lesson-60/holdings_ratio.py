"""14-4 실습 01: 보유 주체별 규모를 표로 정리하고 2,100만 대비 비율 계산 (s144-lab, s144-holdings, 11-2).

기본값은 s144-holdings 슬라이드의 2026년 10월 초 공개 추적 자료(BitcoinTreasuries) 집계(단위 BTC).
직접 조사한 숫자는 CSV(주체,BTC)로 넣는다. 추적 자료는 공시·추정 혼합이다.

    python part5/lesson-60/holdings_ratio.py
    python part5/lesson-60/holdings_ratio.py 내_조사.csv        # 예: "현물 ETF·거래소,1600000"

비율은 float 없이 정수로 계산하고 소수 첫째 자리에서 반올림한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import csv
import unicodedata

SUPPLY = 21_000_000          # 총 공급량 상한 (11-2)
SLIDE = [                    # s144-holdings (2026년 10월 초, BTC)
    ("ETF·거래소", 1_600_000),
    ("상장사 (197개사)", 1_280_000),
    ("국가", 650_000),
    ("비상장사·펀드", 280_000),
]


def pct1(part: int, whole: int) -> str:
    """part/whole을 퍼센트 소수 첫째 자리까지 (반올림, 정수 연산)."""
    q = (part * 1000 * 2 + whole) // (whole * 2)     # 0.1% 단위, 반올림
    return f"{q // 10}.{q % 10}%"


def ljust_w(s: str, width: int) -> str:
    """한글처럼 두 칸을 차지하는 글자를 고려해 왼쪽 정렬."""
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, width - w)


def main():
    rows = SLIDE
    if len(sys.argv) > 1:
        rows = [(r[0], int(r[1].replace(",", "").replace("_", ""))) for r in csv.reader(open(sys.argv[1], encoding="utf-8")) if r]
    w = 20
    print(f"{ljust_w('보유 주체', w)}{'BTC':>12}  2,100만 대비")
    for name, btc in rows:
        print(f"{ljust_w(name, w)}{btc:>12,}  {pct1(btc, SUPPLY):>7}")
    top3 = rows[:3]
    s = sum(b for _, b in top3)
    print(f"{ljust_w('앞 3개 합계', w)}{s:>12,}  {pct1(s, SUPPLY):>7}")
    print("→ 숫자보다 \"이 코인들의 키는 몇 개의 기관이 쥐고 있는가\"를 한 단락으로 정리한다 (실습 03).")


if __name__ == "__main__":
    main()
