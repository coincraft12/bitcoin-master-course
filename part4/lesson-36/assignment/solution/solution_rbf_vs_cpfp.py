"""8강 미니 과제 정답: RBF vs CPFP 비교 (s8-assign).

    python part4/lesson-36/assignment/solution/solution_rbf_vs_cpfp.py          # 예시 수치로 표 (노드 없이)
    python part4/lesson-36/assignment/solution/solution_rbf_vs_cpfp.py run 10   # regtest에서 실험 전체, 목표 10 sat/vB

run은 alice → bob 송금 두 건을 fee_rate 1로 만들고,
  ① 첫 건은 alice가 bumpfee로 목표 수수료율까지,
  ② 둘째 건은 bob이 받은 출력을 쓰는 자식(입력 1·출력 1)으로 패키지 수수료율이 목표가 되게
가속한 뒤 getmempoolentry 결과로 표를 만든다. 마지막에 블록 1개로 확정한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import json
import math
from decimal import Decimal
from lib.rpc import RPC, btc_to_sat, sat_to_btc


def rbf_summary(replacement_entry: dict) -> dict:
    return {"fee": btc_to_sat(replacement_entry["fees"]["base"]), "vsize": replacement_entry["vsize"], "txs": 1}


def cpfp_summary(parent_entry: dict, child_entry: dict) -> dict:
    return {"fee": btc_to_sat(parent_entry["fees"]["base"]) + btc_to_sat(child_entry["fees"]["base"]),
            "vsize": parent_entry["vsize"] + child_entry["vsize"], "txs": 2}


def comparison_table(rbf: dict, cpfp: dict) -> str:
    rows = [f"{'방식':<6}{'총 수수료(sat)':>14}{'총 vsize(vB)':>14}{'실효(sat/vB)':>14}{'트랜잭션 수':>12}"]
    for name, s in (("RBF", rbf), ("CPFP", cpfp)):
        r = (Decimal(s["fee"]) / s["vsize"]).quantize(Decimal("0.01"))
        rows.append(f"{name:<6}{s['fee']:>14}{s['vsize']:>14}{str(r):>14}{s['txs']:>12}")
    rows.append(f"CPFP 추가 비용: {cpfp['fee'] - rbf['fee']} sat (자식 크기만큼)")
    return "\n".join(rows)


def example_entries() -> tuple:
    d = lambda sat: Decimal(sat) / Decimal(100_000_000)
    return ({"vsize": 141, "fees": {"base": d(1410)}},
            {"vsize": 141, "fees": {"base": d(141)}},
            {"vsize": 110, "fees": {"base": d(2369)}})


def run(target: int):
    node, alice, bob, miner = RPC(), RPC(wallet="alice"), RPC(wallet="bob"), RPC(wallet="miner")
    # 01 같은 조건의 송금 두 건
    b1, b2 = bob.getnewaddress(), bob.getnewaddress()
    t1 = alice.send({b1: "0.1"}, None, "unset", 1)["txid"]
    t2 = alice.send({b2: "0.1"}, None, "unset", 1)["txid"]
    print("원본 두 건:", t1, t2)
    # 02-① RBF
    r = alice.bumpfee(t1, {"fee_rate": target})
    repl = node.getmempoolentry(r["txid"])
    # 02-② CPFP: 자식 vsize를 110 vB(P2WPKH 입력 1·출력 1)로 보고 패키지가 목표가 되도록
    p_entry = node.getmempoolentry(t2)
    p_fee, p_vsize = btc_to_sat(p_entry["fees"]["base"]), p_entry["vsize"]
    vout = next(o["n"] for o in node.getrawtransaction(t2, True)["vout"] if o["scriptPubKey"].get("address") == b2)
    child_rate = math.ceil((target * (p_vsize + 110) - p_fee) / 110)
    c = bob.send({bob.getnewaddress(): "0.1"}, None, "unset", child_rate,
                 {"inputs": [{"txid": t2, "vout": vout}], "add_inputs": False, "include_unsafe": True,
                  "subtract_fee_from_outputs": [0]})["txid"]
    c_entry = node.getmempoolentry(c)
    print("getmempoolentry (보고서에 첨부):")
    for name, e in (("RBF 대체본", repl), ("CPFP 부모", node.getmempoolentry(t2)), ("CPFP 자식", c_entry)):
        print(name, json.dumps({k: e[k] for k in ("vsize", "fees")}, default=str))
    print(comparison_table(rbf_summary(repl), cpfp_summary(p_entry, c_entry)))
    miner.generatetoaddress(1, miner.getnewaddress())
    print("블록 1개로 확정. 자식 수수료율", child_rate, "sat/vB, 대체본 수수료", sat_to_btc(btc_to_sat(repl["fees"]["base"])), "BTC")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    else:
        print("예시 수치(실측 아님, 계산 확인용):")
        repl, parent, child = example_entries()
        print(comparison_table(rbf_summary(repl), cpfp_summary(parent, child)))
