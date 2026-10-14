"""10강 미니 과제: 재조직 보고서 (s10-assign) — 전후 비교 표와 트랜잭션 운명 분류.

01 regtest 2노드로 재조직을 만든다 (10-3 실습, part4/lesson-42/reorg_lab.sh 또는 solution의 run)
02 재조직 전후의 getchaintips·멤풀·지갑 잔액 변화를 표로
03 각 변화의 원인을 10-3의 "트랜잭션 운명 네 가지"로 설명 (report_template.md)
선택: 같은 alice 코인을 node2에서 다른 곳으로 보내 이중지불까지 재현

아래 두 함수를 채운다. 스냅샷 형식은 example_snapshots()를 본다. 정답은 solution/solution_reorg_report.py.

    python part4/lesson-43/assignment/exercise_reorg_report.py     # 처음엔 NotImplementedError
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

FATES = ("그대로 확정", "멤풀로 복귀", "충돌로 무효", "코인베이스 보상 소멸")


def tx_fate(in_new_chain: bool, in_mempool: bool, conflicted: bool, is_coinbase: bool) -> str:
    """재조직 뒤 한 트랜잭션의 운명을 FATES 중 하나로."""
    raise NotImplementedError("과제: 10-3 s103-reorg 표의 네 줄을 조건문으로")


def snapshot_table(before: dict, after: dict) -> str:
    """두 스냅샷 → 표. 행: 최고 높이, 활성 tip, valid-fork 가지 수, 멤풀 건수, 지갑별 잔액(trusted/untrusted/immature, sat)."""
    raise NotImplementedError("과제: 같은 항목을 전·후 두 열로")


def example_snapshots() -> tuple:
    """형식 확인용 예시 수치(실측 아님)."""
    before = {"height": 313, "best": "1f9c…", "forks": 0, "mempool": 0,
              "balances": {"miner": (24_000_000_000, 0, 500_000_000_000), "bob": (500_000_000, 0, 0)}}
    after = {"height": 316, "best": "6e2a…", "forks": 1, "mempool": 1,
             "balances": {"miner": (24_000_000_000, 0, 500_000_000_000), "bob": (500_000_000, 30_000_000, 0)}}
    return before, after


if __name__ == "__main__":
    b, a = example_snapshots()
    print(snapshot_table(b, a))
    print("송금 TX:", tx_fate(False, True, False, False))
