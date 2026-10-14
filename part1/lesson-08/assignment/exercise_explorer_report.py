"""1부 미니 과제: 내 노드로 만든 탐색기 리포트 (2-4).

아래 함수 여섯 개를 구현하세요. main()은 그대로 두고 함수만 채우면 리포트가 완성됩니다.
실행(저장소 최상위에서):
    python part1/lesson-08/assignment/exercise_explorer_report.py
정답: solution/explorer_report.py (먼저 스스로 풀어 보세요)

규칙: lib/rpc.py의 RPC를 쓴다. 금액은 btc_to_sat으로 sat 정수로 바꿔 계산한다. float 금지.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from decimal import Decimal

from lib.rpc import RPC, btc_to_sat, sat_to_btc


def recent_blocks(rpc, count=10):
    """최근 count개 블록의 요약을 높이 순 리스트로 돌려준다.
    각 항목은 {"height", "nTx", "size", "weight", "hash"} 키를 가진 dict.
    힌트: getblockcount, getblockhash, getblock(해시, 1). recent_blocks.py를 참고.
    """
    raise NotImplementedError("과제: 최근 블록 목록 만들기")


def find_payments(alice, bob, count=3):
    """alice가 bob에게 보낸 송금 중 블록에 담긴 최근 count건을 [(txid, blockhash), ...]로 돌려준다.
    힌트: alice.listtransactions("*", 1000)의 category == "send" 항목,
          받는 주소가 bob 것인지는 bob.getaddressinfo(주소)["ismine"].
    """
    raise NotImplementedError("과제: alice → bob 송금 찾기")


def guess_change(values_sat):
    """출력 금액(sat 정수) 목록을 받아 잔돈으로 보이는 출력의 인덱스를 돌려준다.
    판단할 수 없으면 None. 잔돈을 알아보는 기준은 스스로 세워 README에 적으세요.
    """
    raise NotImplementedError("과제: 잔돈 추정 기준 세우기")


def fee_sat(rpc, tx):
    """수수료(sat) = 입력이 쓴 이전 출력 금액 합 − 출력 금액 합. 코인베이스면 None.
    tx는 getblock(해시, 3)의 tx 항목. 힌트: verbosity 3에서는 각 vin에 prevout이 붙는다.
    """
    raise NotImplementedError("과제: 수수료 계산 (부분 점수)")


def feerate(fee, vsize):
    """수수료율 sat/vB를 소수 둘째 자리까지 Decimal로 돌려준다."""
    raise NotImplementedError("과제: 수수료율 계산")


def utxo_vs_balance(wallet):
    """(UTXO 개수, UTXO 합계 sat, getbalance sat)를 돌려준다. (1-4)
    힌트: listunspent와 getbalance가 세는 범위(미확정 출력)를 맞추세요.
    """
    raise NotImplementedError("과제: UTXO 합계와 잔액 비교")


def block_tx(rpc, blockhash, txid, cache):
    """getblock(blockhash, 3)에서 txid 트랜잭션을 찾아 돌려준다. 받은 블록은 cache[blockhash]에 둔다."""
    if blockhash not in cache:
        cache[blockhash] = rpc.getblock(blockhash, 3)
    for tx in cache[blockhash]["tx"]:
        if tx["txid"] == txid:
            return tx
    raise RuntimeError(f"블록 {blockhash}에 {txid}가 없습니다")


def main():
    rpc, alice, bob = RPC(), RPC(wallet="alice"), RPC(wallet="bob")

    print("== [2단계] 최근 블록 ==")
    print(f"{'height':>6} {'nTx':>4} {'size':>7} {'weight':>8}  hash")
    for b in recent_blocks(rpc):
        print(f"{b['height']:>6} {b['nTx']:>4} {b['size']:>7} {b['weight']:>8}  {b['hash'][:16]}…")

    payments = find_payments(alice, bob, 3)
    print()
    print(f"== [2·4단계] alice → bob 송금 {len(payments)}건: 입출력, 잔돈 추정, 수수료 ==")
    cache = {}
    for n, (txid, blockhash) in enumerate(payments, 1):
        tx = block_tx(rpc, blockhash, txid, cache)
        values = [btc_to_sat(v["value"]) for v in tx["vout"]]
        guess = guess_change(values)
        print(f"[{n}] {txid}  (블록 {cache[blockhash]['height']})")
        print(f"    입력 {len(tx['vin'])}개, 출력 {len(tx['vout'])}개")
        for v, sat in zip(tx["vout"], values):
            mark = "  ← 잔돈 추정" if v["n"] == guess else ""
            print(f"    출력 {v['n']}: {sat:>11} sat  {v['scriptPubKey'].get('address')}{mark}")
        fee = fee_sat(rpc, tx)
        print(f"    수수료: {fee} sat (vsize {tx['vsize']}, {feerate(fee, tx['vsize'])} sat/vB)")

    print()
    print("== [3단계] alice의 UTXO 합계 vs getbalance ==")
    count, total, balance = utxo_vs_balance(alice)
    print(f"UTXO {count}개 합계: {total} sat = {sat_to_btc(total)} BTC")
    print(f"getbalance      : {balance} sat = {sat_to_btc(balance)} BTC")
    print("일치" if total == balance else f"불일치 (차이 {balance - total} sat)")


if __name__ == "__main__":
    main()
