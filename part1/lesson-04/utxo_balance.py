"""1-4: 잔액 = 내 키로 열 수 있는 UTXO의 합. alice 지갑에서 직접 확인한다.

실행: 저장소 최상위에서 python part1/lesson-04/utxo_balance.py [지갑이름]
준비: env/setup_regtest.sh 실행 완료
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib.rpc import RPC, btc_to_sat, sat_to_btc


def spendable_utxos(utxos):
    """getbalance가 세는 UTXO만 고른다.

    listunspent(0)은 미확정 출력까지 돌려준다. 그중 safe=False인 것
    (남이 보낸 미확정 출력)은 getbalance에 들어가지 않으므로 뺀다.
    내가 만든 미확정 잔돈은 safe=True라서 getbalance에 들어간다.
    """
    return [u for u in utxos if u.get("safe", True)]


def utxo_sum_sat(utxos):
    return sum(btc_to_sat(u["amount"]) for u in utxos)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "alice"
    wallet = RPC(wallet=name)
    utxos = spendable_utxos(wallet.listunspent(0))
    print(f"{name} 지갑의 UTXO {len(utxos)}개")
    for u in sorted(utxos, key=lambda u: (-u["confirmations"], u["txid"], u["vout"])):
        print(f"  {u['txid']}:{u['vout']}  확인 {u['confirmations']:>3}  {btc_to_sat(u['amount']):>12} sat")
    total = utxo_sum_sat(utxos)
    balance = btc_to_sat(wallet.getbalance())
    print(f"UTXO 합계  : {total} sat = {sat_to_btc(total)} BTC")
    print(f"getbalance : {balance} sat = {sat_to_btc(balance)} BTC")
    print("일치" if total == balance else f"불일치 (차이 {balance - total} sat)")


if __name__ == "__main__":
    main()
