"""5강 미니 과제 정답: 세 유형 송금 비교표 (s5-assign 02·03).

    python part3/lesson-22/assignment/solution/solution_compare.py            # 노드 없이: 저장소 demo 세 개
    python part3/lesson-22/assignment/solution/solution_compare.py --node t05/spend_legacy.hex t05/spend_bech32.hex t05/spend_bech32m.hex
      → regtest 노드(txindex=1)에서 이전 출력 금액으로 수수료를 구하고, decoderawtransaction과 다섯 항목을 대조
같은 입력·출력 구성(입력 1개 · bob 0.09 BTC + 잔돈 P2WPKH)이어야 비교가 공정하다.
"""
import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from lib.tx import parse_tx

ROOT = pathlib.Path(__file__).resolve().parents[4]


def measure(hexstr: str) -> dict:
    t = parse_tx(hexstr)
    return {"size": t["size"], "weight": t["weight"], "vsize": t["vsize"], "txid": t["txid"]}


def fee_rate_x100(fee_sat: int, vsize: int) -> int:
    return fee_sat * 100 // vsize


def table(rows: list) -> str:
    lines = [f"{'유형':<8}{'size':>6}{'weight':>8}{'vsize':>7}{'fee(sat)':>10}{'sat/vB':>9}"]
    for name, m, fee in rows:
        r = fee_rate_x100(fee, m["vsize"])
        lines.append(f"{name:<8}{m['size']:>6}{m['weight']:>8}{m['vsize']:>7}{fee:>10}{r // 100:>6}.{r % 100:02d}")
    best = min(rows, key=lambda x: x[1]["vsize"])
    worst = max(rows, key=lambda x: x[1]["vsize"])
    lines.append(f"같은 수수료율이면 가장 싼 유형: {best[0]} (vsize {best[1]['vsize']}) · "
                 f"가장 비싼 {worst[0]}보다 {worst[1]['vsize'] - best[1]['vsize']} vB 작다")
    return "\n".join(lines)


def node_rows(paths):
    from lib.rpc import RPC, btc_to_sat
    rpc = RPC()
    rows = []
    for p in paths:
        hexstr = open(p, encoding="utf-8").read().strip()
        mine = measure(hexstr)
        core = rpc.decoderawtransaction(hexstr)
        ok = all(mine[a] == core[b] for a, b in [("txid", "txid"), ("size", "size"), ("vsize", "vsize"), ("weight", "weight")])
        ok = ok and parse_tx(hexstr)["wtxid"] == core["hash"]
        in_sat = sum(btc_to_sat(rpc.getrawtransaction(i["txid"], True)["vout"][i["vout"]]["value"]) for i in core["vin"])
        fee = in_sat - sum(btc_to_sat(o["value"]) for o in core["vout"])
        print(f"{p}: 파서 = decoderawtransaction {ok}")
        rows.append((pathlib.Path(p).stem.replace("spend_", ""), mine, fee))
    return rows


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--node":
        rows = node_rows(sys.argv[2:])
    else:
        demo = json.load(open(ROOT / "data" / "demo_txs.json", encoding="utf-8"))["txs"]
        rows = [(k, measure(t["hex"]), t["fee_sat"]) for k, t in demo.items()]
    print(table(rows))
