"""8강 미니 과제: RBF vs CPFP 보고서 (s8-assign) — 비교 표 계산 부분.

01 같은 조건의 저수수료 송금 두 건(fee_rate 1)
02 하나는 RBF(bumpfee), 하나는 CPFP(받는 쪽 자식)로 같은 목표 수수료율까지 가속
03 총 수수료·총 vsize·확정까지 필요한 트랜잭션 수를 표로 → 1쪽 보고서

아래 세 함수를 채운다. 입력은 getmempoolentry 결과(dict)다. 금액은 sat 정수로 다룬다.
정답과 실험 자동화는 solution/solution_rbf_vs_cpfp.py.

    python part4/lesson-36/assignment/exercise_rbf_vs_cpfp.py      # 예시 수치로 표 출력 (처음엔 NotImplementedError)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from decimal import Decimal
from lib.rpc import btc_to_sat   # noqa: F401  (풀이에 쓴다)


def rbf_summary(replacement_entry: dict) -> dict:
    """RBF 결과 → {"fee": sat, "vsize": vB, "txs": 확정에 필요한 트랜잭션 수}.
    원본은 멤풀에서 버려지므로 대체본 하나만 센다."""
    raise NotImplementedError("과제: fees.base를 sat로 바꾸고 vsize와 트랜잭션 수 1을 돌려준다")


def cpfp_summary(parent_entry: dict, child_entry: dict) -> dict:
    """CPFP 결과 → {"fee", "vsize", "txs"}. 부모와 자식 둘 다 블록에 들어가야 한다."""
    raise NotImplementedError("과제: 부모·자식 수수료와 vsize를 더하고 트랜잭션 수 2")


def comparison_table(rbf: dict, cpfp: dict) -> str:
    """두 요약을 표(문자열)로. 열: 방식, 총 수수료(sat), 총 vsize(vB), 실효 수수료율(sat/vB), 트랜잭션 수."""
    raise NotImplementedError("과제: 실효 수수료율 = 총 수수료 ÷ 총 vsize")


def example_entries() -> tuple:
    """계산 확인용 예시 수치(실측 아님). 부모 141 vB·1 sat/vB, 목표 10 sat/vB.
    RBF 대체본 141 vB·1,410 sat / CPFP 자식 110 vB·(10 × 251 − 141) = 2,369 sat."""
    d = lambda sat: Decimal(sat) / Decimal(100_000_000)
    replacement = {"vsize": 141, "fees": {"base": d(1410)}}
    parent = {"vsize": 141, "fees": {"base": d(141)}}
    child = {"vsize": 110, "fees": {"base": d(2369)}}
    return replacement, parent, child


if __name__ == "__main__":
    repl, parent, child = example_entries()
    print(comparison_table(rbf_summary(repl), cpfp_summary(parent, child)))
