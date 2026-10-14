#!/usr/bin/env bash
# 1부 미니 과제 1단계: alice → bob 송금 3건을 서로 다른 금액으로 보내고 블록 생성
# 준비: env/setup_regtest.sh 실행 완료(alice 잔액 1.05 BTC 이상)
# 실행: 저장소 최상위에서 part1/lesson-08/assignment/solution/make_payments.sh
set -e
CLI="bitcoin-cli -regtest"

for AMT in 0.1 0.25 0.7; do
  TXID=$($CLI -rpcwallet=alice sendtoaddress "$($CLI -rpcwallet=bob getnewaddress)" $AMT)
  echo "alice → bob $AMT BTC: $TXID"
done
$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "블록 생성: 높이 $($CLI getblockcount)"
