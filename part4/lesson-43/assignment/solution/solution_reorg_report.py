"""10강 미니 과제 정답: 재조직 보고서 (s10-assign).

    python part4/lesson-43/assignment/solution/solution_reorg_report.py                 # 예시 수치로 형식 (노드 없이)
    python part4/lesson-43/assignment/solution/solution_reorg_report.py run            # 2노드 환경에서 재조직 + 표
    python part4/lesson-43/assignment/solution/solution_reorg_report.py run --double-spend   # 선택: 이중지불까지

run 전에 bash part4/lesson-38/two_nodes.sh로 node2를 띄운다.
--double-spend는 분리된 동안 TX와 같은 입력을 alice 자신에게 보내는 트랜잭션 DS를 node2에만 넣고
node2가 채굴하게 한다. 재연결 뒤 TX는 "충돌로 무효"가 된다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import time
from decimal import Decimal
from lib.rpc import RPC, btc_to_sat, sat_to_btc

FATES = ("그대로 확정", "멤풀로 복귀", "충돌로 무효", "코인베이스 보상 소멸")


def tx_fate(in_new_chain: bool, in_mempool: bool, conflicted: bool, is_coinbase: bool) -> str:
    if in_new_chain:
        return FATES[0]
    if is_coinbase:
        return FATES[3]
    if conflicted:
        return FATES[2]
    return FATES[1] if in_mempool else "확인 필요"


def snapshot_table(before: dict, after: dict) -> str:
    rows = [("항목", "재조직 전", "재조직 후")]
    rows += [("최고 높이", before["height"], after["height"]),
             ("활성 tip", before["best"][:12], after["best"][:12]),
             ("valid-fork 가지 수", before["forks"], after["forks"]),
             ("멤풀 건수", before["mempool"], after["mempool"])]
    for w in before["balances"]:
        b, a = before["balances"][w], after["balances"][w]
        rows.append((f"{w} trusted/untrusted/immature (sat)", "/".join(map(str, b)), "/".join(map(str, a))))
    width = max(len(str(r[0])) for r in rows) + 2
    return "\n".join(f"{str(r[0]):<{width}}{str(r[1]):>34}{str(r[2]):>34}" for r in rows)


def example_snapshots() -> tuple:
    before = {"height": 313, "best": "1f9c…", "forks": 0, "mempool": 0,
              "balances": {"miner": (24_000_000_000, 0, 500_000_000_000), "bob": (500_000_000, 0, 0)}}
    after = {"height": 316, "best": "6e2a…", "forks": 1, "mempool": 1,
             "balances": {"miner": (24_000_000_000, 0, 500_000_000_000), "bob": (500_000_000, 30_000_000, 0)}}
    return before, after


def node2() -> RPC:
    r = RPC(datadir="/tmp/node2")
    r.url = "http://127.0.0.1:18556/"          # node2의 RPC 포트 (two_nodes.sh)
    return r


def snapshot(n1: RPC, wallets=("miner", "alice", "bob")) -> dict:
    tips = n1.getchaintips()
    bal = {}
    for w in wallets:
        m = RPC(wallet=w).getbalances()["mine"]
        bal[w] = (btc_to_sat(m["trusted"]), btc_to_sat(m["untrusted_pending"]), btc_to_sat(m["immature"]))
    return {"height": n1.getblockcount(), "best": n1.getbestblockhash(),
            "forks": sum(t["status"] == "valid-fork" for t in tips),
            "mempool": len(n1.getrawmempool()), "balances": bal, "tips": tips}


def run(double_spend: bool):
    n1, n2 = RPC(), node2()
    alice, bob, miner = RPC(wallet="alice"), RPC(wallet="bob"), RPC(wallet="miner")
    assert n1.getbestblockhash() == n2.getbestblockhash(), "두 노드의 tip이 다르다. two_nodes.sh 후 잠시 기다린다"
    before = snapshot(n1)
    n2.setnetworkactive(False)
    tx = alice.sendtoaddress(bob.getnewaddress(), "0.3")
    blocks1 = n1.generatetoaddress(2, miner.getnewaddress())
    if double_spend:
        vin = n1.getrawtransaction(tx, True)["vin"][0]
        value = n1.getrawtransaction(vin["txid"], True)["vout"][vin["vout"]]["value"]
        back = sat_to_btc(btc_to_sat(value) - 10_000)
        raw = n1.createrawtransaction([{"txid": vin["txid"], "vout": vin["vout"]}], [{alice.getnewaddress(): str(back)}])
        ds = alice.signrawtransactionwithwallet(raw)["hex"]
        print("DS(같은 입력을 alice에게) node2에 제출:", n2.sendrawtransaction(ds))
    try:
        n2.createwallet("m2")
    except RuntimeError:
        try:
            n2.loadwallet("m2")
        except RuntimeError:
            pass
    m2 = node2(); m2.url += "wallet/m2"
    n2.generatetoaddress(3, m2.getnewaddress())
    n2.setnetworkactive(True)
    n1.addnode("127.0.0.1:18555", "onetry")
    for _ in range(30):
        if n1.getbestblockhash() == n2.getbestblockhash():
            break
        time.sleep(1)
    after = snapshot(n1)
    print(snapshot_table(before, after))
    print("getchaintips (후):")
    for t in after["tips"]:
        print(f"  {t['status']:<12} height {t['height']} branchlen {t['branchlen']} {t['hash'][:16]}…")
    info = alice.gettransaction(tx)
    fate = tx_fate(info.get("confirmations", 0) > 0, tx in n1.getrawmempool(),
                   info.get("confirmations", 0) < 0 or bool(info.get("walletconflicts")), False)
    print(f"송금 TX {tx[:16]}…: confirmations {info.get('confirmations')} → {fate}")
    for h in blocks1:
        cb = n1.getblock(h, 1)["tx"][0] if n1.getblockheader(h)["confirmations"] >= 0 else None
        print(f"node1이 캔 블록 {h[:16]}… → {tx_fate(False, False, False, True) if cb is None else '새 체인에 남음'}")
    orphans = [t for t in miner.listtransactions("*", 50) if t["category"] == "orphan"]
    print("miner 지갑 orphan 항목:", len(orphans))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        run("--double-spend" in sys.argv)
    else:
        print("예시 수치(실측 아님, 형식 확인용):")
        b, a = example_snapshots()
        print(snapshot_table(b, a))
        print("송금 TX:", tx_fate(False, True, False, False))
        print("버려진 블록 보상:", tx_fate(False, False, False, True))
        print("이중지불된 TX:", tx_fate(False, False, True, False))
