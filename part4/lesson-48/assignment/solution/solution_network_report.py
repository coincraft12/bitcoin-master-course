"""4부 미니 과제 정답: 내 노드로 만든 네트워크 리포트 (s11-assign).

    python part4/lesson-48/assignment/solution/solution_network_report.py              # 예시 수치로 형식 (노드 없이)
    python part4/lesson-48/assignment/solution/solution_network_report.py regtest 300  # regtest 최근 300블록
    python part4/lesson-48/assignment/solution/solution_network_report.py main 1000    # 메인넷 (가산점)

01 블록 크기·weight·트랜잭션 수·수수료율 (getblockstats)
02 블록 간격 분포 (헤더 time)
03 regtest: 보조금 변화 / 메인넷: 코인베이스 태그 상위 10 (11-3 방식)
04 재조직 요약은 10강 보고서(part4/lesson-43/assignment)를 붙인다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import re
from collections import Counter
from decimal import Decimal
from lib.block import subsidy


def block_summary(stats: list[dict]) -> dict:
    n = len(stats)
    paying = [s for s in stats if s["txs"] > 1]
    w = sum(s["txs"] - 1 for s in paying)
    feerate = (Decimal(sum(Decimal(s["avgfeerate"]) * (s["txs"] - 1) for s in paying)) / w).quantize(Decimal("0.01")) if w else Decimal(0)
    return {"blocks": n,
            "avg_size": round(sum(s["total_size"] for s in stats) / n, 1),
            "avg_weight": round(sum(s["total_weight"] for s in stats) / n, 1),
            "avg_txs": round(sum(s["txs"] for s in stats) / n, 2),
            "avg_feerate": feerate}


def interval_stats(times: list[int], bucket: int = 300) -> dict:
    gaps = [b - a for a, b in zip(times, times[1:])]
    hist = Counter((g // bucket) * bucket for g in gaps)
    return {"mean": round(sum(gaps) / len(gaps), 1), "min": min(gaps), "max": max(gaps),
            "hist": dict(sorted(hist.items()))}


def subsidy_changes(stats: list[dict], interval: int = 150) -> list[tuple]:
    out = []
    for a, b in zip(stats, stats[1:]):
        if a["subsidy"] != b["subsidy"]:
            out.append((b["height"], b["subsidy"], b["subsidy"] == subsidy(b["height"], interval)))
    return out


def example_stats() -> list[dict]:
    base = 1_791_970_000
    return [{"height": h, "time": base + t, "total_size": s, "total_weight": w, "txs": n,
             "avgfeerate": f, "subsidy": 5_000_000_000 >> (h // 150)}
            for h, t, s, w, n, f in ((148, 0, 250, 892, 1, 0), (149, 420, 1150, 3664, 4, 5),
                                     (150, 1500, 700, 2340, 3, 12), (151, 1560, 250, 892, 1, 0),
                                     (152, 2400, 980, 3184, 3, 8))]


def coinbase_tags(rpc, heights) -> Counter:
    tags = Counter()
    for h in heights:
        cb = bytes.fromhex(rpc.getblock(rpc.getblockhash(h), 2)["tx"][0]["vin"][0]["coinbase"])
        text = "".join(chr(b) if 32 <= b < 127 else " " for b in cb)
        words = [w for w in re.split(r"\s+", text) if len(w) >= 4]
        tags[words[0] if words else "(unknown)"] += 1
    return tags


def report(stats: list[dict], network: str, rpc=None):
    print("== 01 블록 ==")
    for k, v in block_summary(stats).items():
        print(f"  {k}: {v}")
    print("== 02 블록 간격 (초) ==")
    iv = interval_stats([s["time"] for s in stats])
    print(f"  평균 {iv['mean']} · 최소 {iv['min']} · 최대 {iv['max']}")
    for start, n in iv["hist"].items():
        print(f"  {start:>6}~{start + 299:<6} {'#' * n} {n}")
    if network == "main" and rpc is not None:
        print("== 03 코인베이스 태그 상위 10 ==")
        tags = coinbase_tags(rpc, [s["height"] for s in stats])
        for tag, n in tags.most_common(10):
            print(f"  {tag:<24} {n:>4}  {100 * n / len(stats):.1f}%")
    else:
        print("== 03 보조금 변화 (regtest 반감 주기 150) ==")
        print(f"  구간 {stats[0]['height']}~{stats[-1]['height']} 첫 보조금 {stats[0]['subsidy']} sat")
        for h, s, ok in subsidy_changes(stats):
            print(f"  높이 {h}: {s} sat (subsidy(h, 150)과 {'일치' if ok else '불일치'})")
    print("== 04 재조직 요약: 10강 보고서를 붙인다 ==")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("예시 수치(실측 아님, 형식 확인용):")
        report(example_stats(), "regtest")
        sys.exit(0)
    from lib.rpc import RPC
    network, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 300
    rpc = RPC(network=network)
    tip = rpc.getblockcount()
    keys = ["height", "time", "total_size", "total_weight", "txs", "avgfeerate", "subsidy"]
    stats = [rpc.getblockstats(h, keys) for h in range(max(tip - n + 1, 1), tip + 1)]
    report(stats, network, rpc)
