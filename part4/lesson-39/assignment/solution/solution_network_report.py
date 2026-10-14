"""9강 미니 과제 정답: 내 노드 네트워크 보고서 (s9-assign).

    python part4/lesson-39/assignment/solution/solution_network_report.py                 # 가상 예시 로그로 형식 확인 (노드 없이)
    python part4/lesson-39/assignment/solution/solution_network_report.py regtest \
        /tmp/node2/regtest/debug.log                                                     # 실제 노드 + node2 로그
    python part4/lesson-39/assignment/solution/solution_network_report.py signet         # 피어 분석만

보고서에 붙일 때는 IP 등 개인 정보를 가린다(addr은 출력하지 않는다).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from collections import Counter
import re

MESSAGES = ("inv", "getdata", "tx", "headers", "getheaders", "cmpctblock", "getblocktxn", "blocktxn", "block", "sendcmpct")
LINE = re.compile(r"^(\S+) .*\[net\] (received:|sending) (\w+) \(\d+ bytes\) peer=(\d+)")


def peer_distribution(peers: list[dict]) -> dict:
    return {"방향": Counter("inbound" if p["inbound"] else "outbound" for p in peers),
            "연결 유형": Counter(p["connection_type"] for p in peers),
            "전송 방식": Counter(p.get("transport_protocol_type") for p in peers)}


def parse_net_log(lines: list[str]) -> list[tuple]:
    out = []
    for line in lines:
        m = LINE.match(line.strip())
        if m and m.group(3) in MESSAGES:
            out.append((m.group(1), "received" if m.group(2) == "received:" else "sending", m.group(3), int(m.group(4))))
    return out


def sequence_diagram(events: list[tuple], me: str = "node2", other: str = "node1") -> str:
    rows = []
    for t, direction, msg, peer in events:
        a, b = (other, me) if direction == "received" else (me, other)
        rows.append(f"{t}  {a} ── {msg} ──▶ {b}")
    return "\n".join(rows)


SAMPLE_LOG = [   # 형식 확인용 가상 예시(실제 로그 아님)
    "2026-10-14T05:12:01Z [net] received: inv (37 bytes) peer=0",
    "2026-10-14T05:12:01Z [net] sending getdata (37 bytes) peer=0",
    "2026-10-14T05:12:01Z [net] received: tx (222 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] received: headers (82 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] received: cmpctblock (299 bytes) peer=0",
    "2026-10-14T05:12:04Z [net] sending ping (8 bytes) peer=0",
]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("가상 예시 로그(형식 확인용):")
        print(sequence_diagram(parse_net_log(SAMPLE_LOG)))
        sys.exit(0)
    from lib.rpc import RPC
    dist = peer_distribution(RPC(network=sys.argv[1]).getpeerinfo())
    print("== 01 피어 분포 ==")
    for k, c in dist.items():
        print(f"{k}: {dict(c)}")
    if len(sys.argv) > 2:
        lines = open(sys.argv[2], errors="replace").read().splitlines()
        events = parse_net_log(lines)[-40:]
        print("== 02 전파 시퀀스 (마지막 40개) ==")
        print(sequence_diagram(events))
