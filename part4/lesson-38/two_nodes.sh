#!/usr/bin/env bash
# 9-2 실습 ①: regtest 노드 두 개 연결 (s92-lab1). 저장소 최상위에서 실행.
#   bash part4/lesson-38/two_nodes.sh          # node2를 띄우고 node1과 연결
#   bash part4/lesson-38/two_nodes.sh stop     # node2 종료 ($CLI2 stop)
# node1 = 기존 regtest 노드(기본 datadir, P2P 18444, RPC 18443)
# node2 = /tmp/node2, P2P 18555, RPC 18556. 이 2노드 환경은 9-3, 10-3 실습에서 다시 쓴다.
set -euo pipefail
CLI1="bitcoin-cli -regtest"
CLI2="bitcoin-cli -regtest -datadir=/tmp/node2 -rpcport=18556"

if [ "${1:-}" = "stop" ]; then
  $CLI2 stop
  exit 0
fi

if ! $CLI2 getblockchaininfo >/dev/null 2>&1; then
mkdir -p /tmp/node2
bitcoind -regtest -datadir=/tmp/node2 -port=18555 -rpcport=18556 \
  -fallbackfee=0.0002 -debug=net -daemon
fi
until $CLI2 getblockchaininfo >/dev/null 2>&1; do sleep 1; done   # (저장소 보탬) RPC가 뜰 때까지 대기
CLI1="bitcoin-cli -regtest"
CLI2="bitcoin-cli -regtest -datadir=/tmp/node2 -rpcport=18556"
$CLI1 logging '["net"]'                 # 기존 노드도 네트워크 로그 켜기
$CLI1 addnode 127.0.0.1:18555 onetry
sleep 3
$CLI2 getblockcount; $CLI1 getblockcount  # node2가 블록을 받아 따라잡음
echo "node1이 보는 피어: $($CLI1 getpeerinfo | jq -c '[.[] | {addr, connection_type, inbound}]')"
