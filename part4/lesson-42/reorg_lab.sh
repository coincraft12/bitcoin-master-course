#!/usr/bin/env bash
# 10-3 실습 ①~④: 재조직 재현 — 분리하고 따로 채굴, 다시 연결 (s103-lab1, s103-lab2).
# 9-2의 2노드 환경(bash part4/lesson-38/two_nodes.sh)을 먼저 띄운 뒤 저장소 최상위에서 실행.
#   bash part4/lesson-42/reorg_lab.sh
set -uo pipefail
CLI1="bitcoin-cli -regtest"; CLI2="bitcoin-cli -regtest -datadir=/tmp/node2 -rpcport=18556"
if ! $CLI2 getblockchaininfo >/dev/null 2>&1; then
  echo "node2가 없다 → 먼저 bash part4/lesson-38/two_nodes.sh"; exit 1
fi
echo "# 시작: node1 높이 $($CLI1 getblockcount), node2 높이 $($CLI2 getblockcount) (같아야 한다)"
echo "# miner 잔액(재조직 전): $($CLI1 -rpcwallet=miner getbalances | jq -c .mine)"

# 1) 네트워크 분리
$CLI2 setnetworkactive false
# 2) node1: alice→bob 송금을 담은 블록 2개
TX=$($CLI1 -rpcwallet=alice sendtoaddress $($CLI1 -rpcwallet=bob getnewaddress) 0.3)
$CLI1 generatetoaddress 2 $($CLI1 -rpcwallet=miner getnewaddress)
$CLI1 getrawtransaction $TX true | jq .confirmations          # 2
# 3) node2: 송금 없는 블록 3개 (더 무거운 체인)
$CLI2 -named createwallet wallet_name=m2 >/dev/null 2>&1 || $CLI2 loadwallet m2 >/dev/null 2>&1 || true
$CLI2 generatetoaddress 3 $($CLI2 -rpcwallet=m2 getnewaddress)
BEFORE=$($CLI1 getbestblockhash)

# 4) 재연결
$CLI2 setnetworkactive true
$CLI1 addnode 127.0.0.1:18555 onetry; sleep 5
$CLI1 getchaintips | jq
$CLI1 getrawmempool | jq --arg t "$TX" 'index($t)'
$CLI1 getrawtransaction $TX true | jq .confirmations          # null 또는 0

echo "# getbestblockhash: 재연결 전 $BEFORE → 후 $($CLI1 getbestblockhash) (node2 tip $($CLI2 getbestblockhash))"
echo "# miner 잔액(재조직 후): $($CLI1 -rpcwallet=miner getbalances | jq -c .mine)"
echo "# miner 지갑에서 사라진 블록 보상 (category orphan):"
$CLI1 -rpcwallet=miner listtransactions "*" 20 | jq -c '.[] | select(.category=="orphan") | {category, amount, blockhash}'
echo "# 다음 블록에서 TX 다시 확정"
$CLI1 -rpcwallet=miner -generate 1 >/dev/null
echo "TX 확인 수: $($CLI1 getrawtransaction $TX true | jq .confirmations)"
