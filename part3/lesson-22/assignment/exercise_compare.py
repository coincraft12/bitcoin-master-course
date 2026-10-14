"""5강 미니 과제 02·03: 세 유형 송금 비교표 (s5-assign).

빈 함수 세 개를 채운다. 정답은 solution/solution_compare.py.

    python part3/lesson-22/assignment/exercise_compare.py              # 저장소 demo 세 개로 먼저 확인
    python part3/lesson-22/assignment/exercise_compare.py <hex 파일> <수수료 sat> …   # 내 regtest 송금
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.tx import parse_tx                                   # noqa: F401  (풀이에 쓴다)


def measure(hexstr: str) -> dict:
    """lib/tx.py로 파싱해 {"size", "weight", "vsize", "txid"}를 돌려준다."""
    raise NotImplementedError("과제: parse_tx 결과에서 네 값을 꺼낸다")


def fee_rate_x100(fee_sat: int, vsize: int) -> int:
    """수수료율(sat/vB)의 100배를 정수로 (float 금지). 예: 705 sat, 141 vB → 500"""
    raise NotImplementedError("과제: 정수 나눗셈으로")


def table(rows: list) -> str:
    """rows = [(유형 이름, measure 결과, 수수료 sat)] → 유형·size·weight·vsize·fee·sat/vB 표 문자열, 가장 싼 유형 표시."""
    raise NotImplementedError("과제: 표를 만들고 vsize가 가장 작은 유형을 고른다")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        rows = [(pathlib.Path(h).stem, measure(open(h, encoding="utf-8").read().strip()), int(f)) for h, f in zip(args[::2], args[1::2])]
    else:
        demo = json.load(open(pathlib.Path(__file__).resolve().parents[3] / "data" / "demo_txs.json", encoding="utf-8"))["txs"]
        rows = [(k, measure(t["hex"]), t["fee_sat"]) for k, t in demo.items()]
    print(table(rows))
