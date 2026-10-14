#!/usr/bin/env bash
# 9-2 실습 ②: 전파 관찰 (s92-lab2). two_nodes.sh로 node2를 띄운 뒤 저장소 최상위에서 실행.
#   bash part4/lesson-38/watch_spread.sh
set -euo pipefail
CLI1="bitcoin-cli -regtest"
CLI2="bitcoin-cli -regtest -datadir=/tmp/node2 -rpcport=18556"

echo "# 01 node1에서 alice → bob 송금, node2 멤풀에 같은 txid가 나타나는지"
TX=$($CLI1 -rpcwallet=alice sendtoaddress "$($CLI1 -rpcwallet=bob getnewaddress)" 0.01)
echo "TX=$TX"
for i in $(seq 1 30); do
  if $CLI2 getrawmempool | jq -e --arg t "$TX" 'index($t) != null' >/dev/null; then
    echo "node2 멤풀에 도착: ${i}초 안쪽 (바로 안 나오는 이유 = 무작위 지연)"
    break
  fi
  sleep 1
done

echo "# 02 node1에서 블록 하나 생성 → node2 높이가 따라오는지"
$CLI1 -rpcwallet=miner -generate 1 >/dev/null
sleep 2
echo "node1 높이 $($CLI1 getblockcount) · node2 높이 $($CLI2 getblockcount)"

echo "# 03 node2 로그에서 메시지 기록 → 시퀀스 그림(inv → getdata → tx)과 대조"
grep -E "received: (inv|getdata|tx|cmpctblock|headers)" /tmp/node2/regtest/debug.log | tail -20
echo "끝나면 \$CLI2 stop (bash part4/lesson-38/two_nodes.sh stop) · 이 2노드 환경은 10-3 재조직 실습에서 다시 쓴다"
