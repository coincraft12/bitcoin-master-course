#!/usr/bin/env bash
# 7-4 LAB ① (s74-lab1): P2TR 코인 하나짜리 지갑 tr1에서 지출을 만들고, 전파 전에 내 코드로 검증. 저장소 최상위에서 실행.
#   bash part3/lesson-31/tr1_lab.sh        → ./tr1_spend.hex, ./prevouts.json → verify_keypath.py, scope.py
set -euo pipefail
CLI="bitcoin-cli -regtest"
$CLI createwallet tr1 > /dev/null 2>&1 || $CLI loadwallet tr1 > /dev/null 2>&1 || true
A=$($CLI -rpcwallet=tr1 getnewaddress "" bech32m)
$CLI -rpcwallet=miner sendtoaddress "$A" 0.7 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null
PSBT=$($CLI -rpcwallet=tr1 walletcreatefundedpsbt '[]' \
  "[{\"$($CLI -rpcwallet=bob getnewaddress)\":0.3}]" | jq -r .psbt)
$CLI decodepsbt "$PSBT" | jq '[.inputs[].witness_utxo]' > prevouts.json
SIGNED=$($CLI -rpcwallet=tr1 walletprocesspsbt "$PSBT" | jq -r .psbt)
$CLI finalizepsbt "$SIGNED" | jq -r .hex > tr1_spend.hex
cat prevouts.json
# ② 노드가 하는 검증을 내 코드로, ③ sighash 범위 체감
python3 part3/lesson-31/verify_keypath.py
python3 part3/lesson-31/scope.py
