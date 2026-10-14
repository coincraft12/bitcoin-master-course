#!/usr/bin/env bash
# 9-3 실습: 블록 필터와 v2 전송 확인 (s93-lab). 저장소 최상위에서 실행.
#   bash part4/lesson-39/filters_v2.sh
# 필요: regtest node1(bitcoin.conf에 blockfilterindex=1, 2-1), 9-2의 node2(two_nodes.sh), jq.
# signet 노드가 떠 있으면 signet 최신 블록 필터도 함께 본다.
set -uo pipefail

echo "######## 01 최신 블록 필터 ########"
CLI="bitcoin-cli -regtest"
HASH=$($CLI getbestblockhash)
$CLI getblockfilter $HASH | jq '{filter, header}'
$CLI getindexinfo | jq
echo "블록 $(($($CLI getblock $HASH 0 | wc -c) / 2)) 바이트 vs 필터 $(($($CLI getblockfilter $HASH | jq -r .filter | wc -c) / 2)) 바이트 (줄바꿈 1글자 포함 근사)"

if bitcoin-cli -signet getblockchaininfo >/dev/null 2>&1; then
  echo "######## (signet) 최신 블록 필터 ########"
  SCLI="bitcoin-cli -signet"
  SH=$($SCLI getbestblockhash)
  echo "signet 블록 $($SCLI getblock "$SH" 1 | jq .size) 바이트 vs 필터 $(($($SCLI getblockfilter "$SH" | jq -r .filter | wc -c) / 2)) 바이트"
fi

echo "######## 02 v2 전송 확인 (9-2 2노드 환경에서) ########"
$CLI getpeerinfo | jq '.[] | {addr, transport_protocol_type}'   # v2
# node2를 -v2transport=0으로 재시작 후 다시 → v1
CLI2="bitcoin-cli -regtest -datadir=/tmp/node2 -rpcport=18556"
if $CLI2 getblockchaininfo >/dev/null 2>&1; then
  $CLI2 stop >/dev/null
  while $CLI2 getblockchaininfo >/dev/null 2>&1; do sleep 1; done
  sleep 2
  bitcoind -regtest -datadir=/tmp/node2 -port=18555 -rpcport=18556 -bind=0.0.0.0:18555 \
    -fallbackfee=0.0002 -debug=net -daemon -v2transport=0   # -bind: Tor 리스너(18556)와 RPC 포트 충돌 방지 (ERRATA.md)
  until $CLI2 getblockchaininfo >/dev/null 2>&1; do sleep 1; done
  $CLI addnode 127.0.0.1:18555 onetry
  sleep 3
  $CLI getpeerinfo | jq '.[] | {addr, transport_protocol_type}'   # v1
  echo "→ 다음 실습(10-3)을 위해 node2를 기본 설정으로 되돌리려면:"
  echo "   bash part4/lesson-38/two_nodes.sh stop && bash part4/lesson-38/two_nodes.sh"
else
  echo "node2가 없다 → 먼저 bash part4/lesson-38/two_nodes.sh"
fi

echo "######## 03 (선택, 메인넷·signet) Tor 설정 후 onion 주소 확인 ########"
echo "bitcoin-cli -signet getnetworkinfo | jq .localaddresses"
