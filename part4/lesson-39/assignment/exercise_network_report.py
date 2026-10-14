"""9강 미니 과제: 내 노드 네트워크 보고서 (s9-assign) — 자동 분석 부분.

01 getpeerinfo 분석: 방향·연결 유형·전송 방식 분포
02 2노드 환경의 전파 로그(트랜잭션 1건, 블록 1개)를 시퀀스 그림으로
03 내 지갑이 SPV·블록 필터·서버 질의 중 무엇인지와 노출 정보 1문단 → report_template.md에 직접 쓴다

아래 세 함수를 채운다. 정답은 solution/solution_network_report.py.

    python part4/lesson-39/assignment/exercise_network_report.py       # 처음엔 NotImplementedError
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from collections import Counter   # noqa: F401  (풀이에 쓴다)
import re                         # noqa: F401

MESSAGES = ("inv", "getdata", "tx", "headers", "getheaders", "cmpctblock", "getblocktxn", "blocktxn", "block", "sendcmpct")


def peer_distribution(peers: list[dict]) -> dict:
    """getpeerinfo 결과 → {"방향": Counter, "연결 유형": Counter, "전송 방식": Counter}"""
    raise NotImplementedError("과제: 9-1 my_peers.py의 Counter 세 줄을 함수로")


def parse_net_log(lines: list[str]) -> list[tuple]:
    """debug.log 줄 → [(시각, "received"|"sending", 메시지, peer 번호), ...]. MESSAGES에 있는 것만.
    줄 예: '... [net] received: inv (37 bytes) peer=0', '... [net] sending getdata (37 bytes) peer=0'"""
    raise NotImplementedError("과제: 정규식으로 received:/sending 뒤의 메시지 이름과 peer=번호를 뽑는다")


def sequence_diagram(events: list[tuple], me: str = "node2", other: str = "node1") -> str:
    """parse_net_log 결과 → 한 줄에 화살표 하나. received는 other → me, sending은 me → other."""
    raise NotImplementedError("과제: 예) 'node1 ── inv ──▶ node2'")


SAMPLE_LOG = [   # 형식 확인용 가상 예시(실제 로그 아님)
    "2026-10-14T05:12:01Z [net] received: inv (37 bytes) peer=0",
    "2026-10-14T05:12:01Z [net] sending getdata (37 bytes) peer=0",
    "2026-10-14T05:12:01Z [net] received: tx (222 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] received: headers (82 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] received: cmpctblock (299 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] sending ping (8 bytes) peer=0",
]

if __name__ == "__main__":
    print(sequence_diagram(parse_net_log(SAMPLE_LOG)))
