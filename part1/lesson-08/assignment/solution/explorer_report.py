"""1부 미니 과제 정답: 내 노드로 만든 탐색기 리포트 (2-4).

실행(저장소 최상위에서):
    part1/lesson-08/assignment/solution/make_payments.sh      # 1단계: 송금 3건 + 블록
    python part1/lesson-08/assignment/solution/explorer_report.py

리포트 내용
    2단계  최근 블록 목록, 각 송금의 입력·출력 수, 잔돈으로 보이는 출력
    3단계  alice의 UTXO 합계 = getbalance (1-4)
    4단계  수수료 (getblock verbosity 3, 5-1 예습)
금액은 모두 sat 정수로 계산한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))

from decimal import Decimal

from lib.rpc import RPC, btc_to_sat, sat_to_btc


# ---------------------------------------------------------------- 2단계: 블록 목록

def recent_blocks(rpc, count=10):
    """최근 count개 블록의 요약(height, nTx, size, weight, hash)을 높이 순으로 돌려준다."""
    tip = rpc.getblockcount()
    rows = []
    for h in range(max(0, tip - count + 1), tip + 1):
        b = rpc.getblock(rpc.getblockhash(h), 1)
        rows.append({k: b[k] for k in ("height", "nTx", "size", "weight", "hash")})
    return rows


# ---------------------------------------------------------------- 2단계: 송금 찾기

def find_payments(alice, bob, count=3):
    """alice가 bob에게 보낸 송금 중 블록에 담긴 최근 count건을 [(txid, blockhash)]로 돌려준다.

    alice 지갑의 'send' 항목 가운데 받는 주소가 bob 지갑 소유인 것만 고른다.
    """
    entries = alice.listtransactions("*", 1000)
    found = {}
    for e in entries:
        if e.get("category") != "send" or "blockhash" not in e:
            continue
        addr = e.get("address")
        if addr and bob.getaddressinfo(addr).get("ismine"):
            found.setdefault(e["txid"], (e.get("blockheight", -1), e.get("time", 0), e["blockhash"]))
    ordered = sorted(found.items(), key=lambda kv: (kv[1][0], kv[1][1], kv[0]))
    return [(txid, info[2]) for txid, info in ordered[-count:]]


def block_tx(rpc, blockhash, txid, cache):
    """getblock verbosity 3으로 블록을 받아 그 안의 txid 트랜잭션을 돌려준다. 블록은 cache에 둔다."""
    if blockhash not in cache:
        cache[blockhash] = rpc.getblock(blockhash, 3)
    for tx in cache[blockhash]["tx"]:
        if tx["txid"] == txid:
            return tx
    raise RuntimeError(f"블록 {blockhash}에 {txid}가 없습니다")


# ---------------------------------------------------------------- 2단계: 잔돈 추정

def trailing_zeros(sat):
    """sat 금액의 끝자리 0 개수. 0 sat은 0으로 본다."""
    if sat == 0:
        return 0
    n = 0
    while sat % 10 == 0:
        sat //= 10
        n += 1
    return n


def guess_change(values_sat):
    """출력 금액(sat) 목록에서 잔돈으로 보이는 출력의 인덱스를 돌려준다. 판단할 수 없으면 None.

    기준(둥근 금액 휴리스틱): 사람이 정하는 지급액은 0.1 BTC처럼 끝자리가 0으로 끝나기 쉽고,
    잔돈은 '입력 − 지급 − 수수료'라 끝자리가 지저분하다. 끝자리 0이 가장 적은 출력이
    하나뿐이면 그것을 잔돈으로 본다. 출력이 1개이거나 동률이면 None.
    """
    if len(values_sat) < 2:
        return None
    zeros = [trailing_zeros(v) for v in values_sat]
    low = min(zeros)
    candidates = [i for i, z in enumerate(zeros) if z == low]
    return candidates[0] if len(candidates) == 1 else None


# ---------------------------------------------------------------- 4단계: 수수료

def prevout_value_sat(rpc, vin):
    """입력이 쓴 이전 출력의 금액(sat). verbosity 3의 prevout을 쓰고, 없으면 이전 트랜잭션을 조회한다."""
    if "prevout" in vin:
        return btc_to_sat(vin["prevout"]["value"])
    prev = rpc.getrawtransaction(vin["txid"], True)
    return btc_to_sat(prev["vout"][vin["vout"]]["value"])


def fee_sat(rpc, tx):
    """수수료 = 입력 합 − 출력 합 (sat). 코인베이스는 None."""
    if any("coinbase" in vin for vin in tx["vin"]):
        return None
    total_in = sum(prevout_value_sat(rpc, vin) for vin in tx["vin"])
    total_out = sum(btc_to_sat(v["value"]) for v in tx["vout"])
    return total_in - total_out


def feerate(fee, vsize):
    """sat/vB를 소수 둘째 자리까지 Decimal로. float를 쓰지 않는다."""
    return (Decimal(fee) / Decimal(vsize)).quantize(Decimal("0.01"))


# ---------------------------------------------------------------- 3단계: UTXO 합 = 잔액

def utxo_vs_balance(wallet):
    """(UTXO 개수, UTXO 합계 sat, getbalance sat)를 돌려준다.

    listunspent(0)으로 미확정 출력까지 받되, getbalance가 세지 않는
    safe=False 출력(남이 보낸 미확정 출력)은 뺀다.
    """
    utxos = [u for u in wallet.listunspent(0) if u.get("safe", True)]
    total = sum(btc_to_sat(u["amount"]) for u in utxos)
    return len(utxos), total, btc_to_sat(wallet.getbalance())


# ---------------------------------------------------------------- 리포트

def owner_label(addr, alice, bob):
    if addr is None:
        return "주소 없음"
    if bob.getaddressinfo(addr).get("ismine"):
        return "bob"
    if alice.getaddressinfo(addr).get("ismine"):
        return "alice"
    return "기타"


def main():
    rpc, alice, bob = RPC(), RPC(wallet="alice"), RPC(wallet="bob")

    print("== [2단계] 최근 블록 ==")
    print(f"{'height':>6} {'nTx':>4} {'size':>7} {'weight':>8}  hash")
    for b in recent_blocks(rpc):
        print(f"{b['height']:>6} {b['nTx']:>4} {b['size']:>7} {b['weight']:>8}  {b['hash'][:16]}…")

    payments = find_payments(alice, bob, 3)
    print()
    print(f"== [2·4단계] alice → bob 송금 {len(payments)}건: 입출력, 잔돈 추정, 수수료 ==")
    if not payments:
        print("블록에 담긴 alice → bob 송금이 없습니다. make_payments.sh를 먼저 실행하세요.")
    cache = {}
    total_fee = 0
    fee_ok = True
    for n, (txid, blockhash) in enumerate(payments, 1):
        tx = block_tx(rpc, blockhash, txid, cache)
        height = cache[blockhash]["height"]
        values = [btc_to_sat(v["value"]) for v in tx["vout"]]
        print(f"[{n}] {txid}  (블록 {height})")
        print(f"    입력 {len(tx['vin'])}개, 출력 {len(tx['vout'])}개")
        guess = guess_change(values)
        for v, sat in zip(tx["vout"], values):
            addr = v["scriptPubKey"].get("address")
            mark = "  ← 잔돈 추정" if v["n"] == guess else ""
            print(f"    출력 {v['n']}: {sat:>11} sat  {addr}{mark}")
        if guess is None:
            print("    잔돈 추정: 판단 불가 (끝자리 0 개수가 같음)")
        else:
            addr = tx["vout"][guess]["scriptPubKey"].get("address")
            owner = owner_label(addr, alice, bob)
            verdict = "맞음" if owner == "alice" else "틀림"
            print(f"    잔돈 추정: 출력 {guess} (끝자리 0이 가장 적은 금액) / 지갑 확인: {owner} 소유 → {verdict}")
        fee = fee_sat(rpc, tx)
        total_fee += fee
        line = f"    수수료: {fee} sat (vsize {tx['vsize']}, {feerate(fee, tx['vsize'])} sat/vB)"
        if "fee" in tx:
            same = btc_to_sat(tx["fee"]) == fee
            fee_ok = fee_ok and same
            line += " · 노드 fee 필드와 " + ("일치" if same else f"불일치({btc_to_sat(tx['fee'])} sat)")
        print(line)
    if payments:
        print(f"    수수료 합계: {total_fee} sat = {sat_to_btc(total_fee)} BTC"
              + ("" if fee_ok else " (노드 값과 다른 항목 있음)"))

    print()
    print("== [3단계] alice의 UTXO 합계 vs getbalance ==")
    count, total, balance = utxo_vs_balance(alice)
    print(f"UTXO {count}개 합계: {total} sat = {sat_to_btc(total)} BTC")
    print(f"getbalance      : {balance} sat = {sat_to_btc(balance)} BTC")
    print("일치" if total == balance else f"불일치 (차이 {balance - total} sat)")


if __name__ == "__main__":
    main()
