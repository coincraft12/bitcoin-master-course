#!/usr/bin/env bash
# 5-4 LAB ①~⑥ (s54-lab1~3): 서명 지갑(signer)과 워치온리 지갑(watch) 사이의 PSBT 송금. 저장소 최상위에서 실행.
#   bash part3/lesson-22/psbt_lab.sh
# 같은 regtest 노드지만 어느 지갑에서 어떤 명령을 실행하는지 엄격히 구분한다.
set -euo pipefail
CLI="bitcoin-cli -regtest"

# 1. 지갑 두 개 (이미 있으면 불러오기만)
$CLI createwallet signer > /dev/null 2>&1 || $CLI loadwallet signer > /dev/null 2>&1 || true
$CLI -named createwallet wallet_name=watch disable_private_keys=true blank=true > /dev/null 2>&1 \
  || $CLI loadwallet watch > /dev/null 2>&1 || true

# 2. signer의 공개 wpkh 디스크립터(받는용·잔돈용) → watch로
$CLI -rpcwallet=signer listdescriptors \
  | jq '.descriptors[] | select(.desc | startswith("wpkh("))'
RECV=$($CLI -rpcwallet=signer listdescriptors | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == false) | .desc')
CHG=$($CLI -rpcwallet=signer listdescriptors | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == true) | .desc')
$CLI -rpcwallet=watch importdescriptors "[{\"desc\":\"$RECV\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$CHG\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c '[.[].success]'
echo "signer 주소: $($CLI -rpcwallet=signer getnewaddress "" bech32)"
echo "watch  주소: $($CLI -rpcwallet=watch getnewaddress "" bech32)   ← 같아야 한다 (xpub만으로 파생, 4-2)"

# 3. watch 주소로 입금
ADDR=$($CLI -rpcwallet=watch getnewaddress "" bech32)
$CLI -rpcwallet=miner sendtoaddress "$ADDR" 1 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null; $CLI -rpcwallet=watch getbalances | jq -c .

# 4. watch: Creator + Updater
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
PSBT=$($CLI -rpcwallet=watch walletcreatefundedpsbt \
  '[]' "[{\"$BOB\":0.2}]" 0 '{"fee_rate":5}' | jq -r .psbt)
$CLI decodepsbt "$PSBT" | jq '{inputs: [.inputs[].witness_utxo], fee}'
$CLI decodepsbt "$PSBT" | jq -c '[.inputs[].bip32_derivs[] | {master_fingerprint, path}]'
$CLI analyzepsbt "$PSBT" | jq -c '{next}'

# 5. signer: Signer + Finalizer
SIGNED=$($CLI -rpcwallet=signer walletprocesspsbt "$PSBT" | jq -r .psbt)
$CLI analyzepsbt "$SIGNED" | jq -c '{next}'   # next: extractor

# 6. watch 쪽: Extractor → 전파
HEX=$($CLI finalizepsbt "$SIGNED" | jq -r .hex)
$CLI sendrawtransaction "$HEX"
$CLI -rpcwallet=miner -generate 1 > /dev/null
echo "$PSBT" > psbt_unsigned.b64     # 심화 과제(받는 주소 바꿔 decodepsbt 비교)용으로 남겨 둔다
