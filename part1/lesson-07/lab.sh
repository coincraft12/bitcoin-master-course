#!/usr/bin/env bash
# 2-3 LAB: 블록에서 트랜잭션까지
# 준비: env/setup_regtest.sh 실행 완료, jq·curl 설치
# 실행: 저장소 최상위에서 part1/lesson-07/lab.sh
set -e

# ---- 1. 조회 연쇄: 체인 → 블록 → 트랜잭션 ----
CLI="bitcoin-cli -regtest"
$CLI getblockchaininfo | jq '{chain, blocks, bestblockhash}'
HASH=$($CLI getblockhash $($CLI getblockcount))
$CLI getblock $HASH 1 | jq '{height, time, nTx, size, weight, tx}'
TXID=$($CLI getblock $HASH 1 | jq -r '.tx[0]')
$CLI getrawtransaction $TXID true | jq '{txid, vin, vout}'   # vin에 coinbase

# ---- 2. curl로 같은 RPC 직접 호출 → result, error, id 확인 ----
# 데이터 디렉터리 경로는 운영체제마다 다르다(2-1). macOS는 BITCOIN_DATADIR을 지정한다(env/README.md).
COOKIE=$(cat "${BITCOIN_DATADIR:-$HOME/.bitcoin}/regtest/.cookie")
curl -s --user "$COOKIE" -H 'content-type: text/plain;' http://127.0.0.1:18443/ \
  --data-binary '{"jsonrpc":"1.0","id":"cc","method":"getblockcount","params":[]}'

# ---- 과제 1: 2-2에서 alice와 bob에게 보낸 송금이 어느 블록에 있는가 ----
echo "== alice·bob이 받은 송금과 담긴 블록 =="
for W in alice bob; do
  $CLI -rpcwallet=$W listtransactions | jq -c --arg w "$W" \
    '.[] | select(.category == "receive") | {wallet: $w, txid, amount, blockheight, blockhash}'
done

# ---- 과제 2: verbosity를 0, 1, 2로 바꿔 출력 크기 비교 (바이트) ----
echo "== getblock verbosity별 출력 크기 (최신 블록) =="
for V in 0 1 2; do
  echo "verbosity $V: $($CLI getblock $HASH $V | wc -c) bytes"
done

# ---- 과제 3: 존재하지 않는 메서드로 보내 error 필드가 채워지는 것 보기 ----
echo "== 없는 메서드 호출 =="
curl -s --user "$COOKIE" -H 'content-type: text/plain;' http://127.0.0.1:18443/ \
  --data-binary '{"jsonrpc":"1.0","id":"cc","method":"getblockcounts","params":[]}'
