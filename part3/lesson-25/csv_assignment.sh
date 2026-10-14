#!/usr/bin/env bash
# 6-3 과제 · CSV 버전 (s63-lab3): wsh(and_v(v:pk($TPRV/8/*),older(10))). 저장소 최상위에서 실행.
#   bash part3/lesson-25/csv_assignment.sh
# 입금 확정 직후와 10블록 뒤의 결과를 비교해 제출한다. regtest 전용 키만.
set -euo pipefail
CLI="bitcoin-cli -regtest"
TPRV=$($CLI -rpcwallet=participant_1 listdescriptors true \
  | jq -r '.descriptors[0].desc' | grep -o 'tprv[a-zA-Z0-9]*')
DESC="wsh(and_v(v:pk($TPRV/8/*),older(10)))"
DESC="$DESC#$($CLI getdescriptorinfo "$DESC" | jq -r .checksum)"
$CLI -named createwallet wallet_name=csv blank=true > /dev/null 2>&1 || $CLI loadwallet csv > /dev/null 2>&1 || true
$CLI -rpcwallet=csv importdescriptors \
  "[{\"desc\":\"$DESC\",\"timestamp\":\"now\",\"range\":[0,5]}]" | jq -c '[.[].success]'
ADDR=$($CLI deriveaddresses "$DESC" "[0,0]" | jq -r '.[0]')
CHG=$($CLI deriveaddresses "$DESC" "[1,1]" | jq -r '.[0]')
TXID=$($CLI -rpcwallet=miner sendtoaddress "$ADDR" 1)
$CLI -rpcwallet=miner -generate 1 > /dev/null
VOUT=$($CLI getrawtransaction "$TXID" true | jq --arg a "$ADDR" '.vout[] | select(.scriptPubKey.address == $a) | .n')
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)

# 입력에 sequence 10 명시 (BIP68: 확정 후 10블록), version 2는 Core 기본값
P=$($CLI -rpcwallet=csv walletcreatefundedpsbt \
  "[{\"txid\":\"$TXID\",\"vout\":$VOUT,\"sequence\":10}]" "[{\"$BOB\":0.5}]" 0 \
  "{\"changeAddress\":\"$CHG\",\"add_inputs\":false}" | jq -r .psbt)
S=$($CLI -rpcwallet=csv walletprocesspsbt "$P" | jq -r .psbt)
HEX=$($CLI finalizepsbt "$S" | jq -r .hex)
echo "== 확정 직후 (1 confirmation) =="
$CLI testmempoolaccept "[\"$HEX\"]" | jq -c '.[0] | {allowed, "reject-reason"}'
$CLI -rpcwallet=miner -generate 9 > /dev/null
echo "== 10 confirmations 뒤 (다음 블록이 11번째) =="
$CLI testmempoolaccept "[\"$HEX\"]" | jq -c '.[0] | {allowed, "reject-reason"}'
$CLI sendrawtransaction "$HEX"
$CLI -rpcwallet=miner -generate 1 > /dev/null
