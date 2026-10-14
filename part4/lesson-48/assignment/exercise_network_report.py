"""4부 미니 과제: 내 노드로 만든 네트워크 리포트 (s11-assign) — 자동 계산 스크립트.

regtest(메인넷 노드가 있으면 메인넷)에서 다음을 자동으로 계산한다.
01 최근 블록 N개의 평균 크기·weight, 블록당 트랜잭션 수, 평균 수수료율 (8-1)
02 블록 간 시간 간격 분포와 평균 (11-1 무기억성 확인)
03 코인베이스 태그 상위 집계 또는 regtest 보조금 변화 (11-2·11-3)
04 10강 재조직 실습 결과 요약 (10-3) → report_template.md에 직접 쓴다

아래 세 함수를 채운다. 입력은 getblockstats 결과(dict)의 목록이다. 정답은 solution/solution_network_report.py.

    python part4/lesson-48/assignment/exercise_network_report.py     # 처음엔 NotImplementedError
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from lib.block import subsidy   # noqa: F401  (풀이에 쓴다)


def block_summary(stats: list[dict]) -> dict:
    """{"blocks", "avg_size", "avg_weight", "avg_txs", "avg_feerate"} — avg_feerate는 블록들의
    getblockstats avgfeerate(sat/vB)를 트랜잭션 수로 가중 평균(코인베이스만 있는 블록은 제외)."""
    raise NotImplementedError("과제: total_size, total_weight, txs, avgfeerate 필드를 쓴다")


def interval_stats(times: list[int], bucket: int = 300) -> dict:
    """블록 time 목록(오름차순) → {"mean", "min", "max", "hist": {구간 시작(초): 개수}}.
    무기억성이면 짧은 간격이 가장 많고 긴 간격으로 갈수록 줄어드는 모양(지수분포)."""
    raise NotImplementedError("과제: 이웃한 time의 차이를 bucket초 단위로 센다")


def subsidy_changes(stats: list[dict], interval: int = 150) -> list[tuple]:
    """보조금이 바뀌는 높이 목록 [(높이, 보조금 sat), ...]과 subsidy(h, interval) 일치 여부."""
    raise NotImplementedError("과제: 이웃 블록의 subsidy가 달라지는 곳을 찾는다")


def example_stats() -> list[dict]:
    """형식 확인용 예시 수치(실측 아님): 높이 148~152, 10분 간격 근처."""
    base = 1_791_970_000
    return [{"height": h, "time": base + t, "total_size": s, "total_weight": w, "txs": n,
             "avgfeerate": f, "subsidy": 5_000_000_000 >> (h // 150)}
            for h, t, s, w, n, f in ((148, 0, 250, 892, 1, 0), (149, 420, 1150, 3664, 4, 5),
                                     (150, 1500, 700, 2340, 3, 12), (151, 1560, 250, 892, 1, 0),
                                     (152, 2400, 980, 3184, 3, 8))]


if __name__ == "__main__":
    st = example_stats()
    print(block_summary(st))
    print(interval_stats([s["time"] for s in st]))
    print(subsidy_changes(st))
