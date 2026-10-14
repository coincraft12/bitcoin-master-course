#!/usr/bin/env bash
# 6-5 LAB ①~④ (s65-lab1~3, s65-code): NUMS 내부키 아래 {pk(B), pk(C)} → participant_3 혼자 C 리프로 지출 → witness 해부 → 약속 검증.
# 저장소 최상위에서 실행. 6-2(lesson-24)에서 저장한 xpub_2.txt, xpub_3.txt와 participant_3 지갑이 필요하다.
#   bash part3/lesson-27/tapscript_lab.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"

# ① 스크립트 경로로만 쓸 수 있는 출력
NUMS=50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0
X2=$(cat xpub_2.txt); X3=$(cat xpub_3.txt)                  # 6-2에서 저장
EXT="tr($NUMS,{pk($X2/0/*),pk($X3/0/*)})"
INT="tr($NUMS,{pk($X2/1/*),pk($X3/1/*)})"
EXT="$EXT#$($CLI getdescriptorinfo "$EXT" | jq -r .checksum)"
INT="$INT#$($CLI getdescriptorinfo "$INT" | jq -r .checksum)"
$CLI -named createwallet wallet_name=tapscript disable_private_keys=true blank=true > /dev/null 2>&1 \
  || $CLI loadwallet tapscript > /dev/null 2>&1 || true
$CLI -rpcwallet=tapscript importdescriptors "[
  {\"desc\":\"$EXT\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$INT\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c '[.[].success]'

# ② participant_3만 서명
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
TS_ADDR=$($CLI -rpcwallet=tapscript getnewaddress "" bech32m)
$CLI -rpcwallet=miner sendtoaddress "$TS_ADDR" 1 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null
PSBT=$($CLI -rpcwallet=tapscript walletcreatefundedpsbt \
  '[]' "[{\"$BOB\":0.3}]" 0 '{"fee_rate":5}' | jq -r .psbt)
$CLI decodepsbt "$PSBT" | jq '.inputs[0] | {taproot_scripts, taproot_bip32_derivs}'
SIGNED=$($CLI -rpcwallet=participant_3 walletprocesspsbt "$PSBT" | jq -r .psbt)
HEX=$($CLI finalizepsbt "$SIGNED" | jq -r .hex)
$CLI sendrawtransaction "$HEX"

# ③ witness 해부: 서명 64B · 리프 스크립트 34B · 컨트롤 블록 65B
$CLI decoderawtransaction "$HEX" \
  | jq '.vin[0].txinwitness | map({hex: ., bytes: (length/2)})'
LEAF=$($CLI decoderawtransaction "$HEX" | jq -r '.vin[0].txinwitness[1]')
CTRL=$($CLI decoderawtransaction "$HEX" | jq -r '.vin[0].txinwitness[2]')
$CLI decodescript "$LEAF" | jq -r .asm

# ④ 약속 직접 검증: 지출된 출력의 scriptPubKey + witness 두 번째·세 번째 항목
PREV=$($CLI decoderawtransaction "$HEX" | jq -r '.vin[0] | "\(.txid) \(.vout)"')
SPK=$($CLI getrawtransaction "${PREV% *}" true | jq -r ".vout[${PREV#* }].scriptPubKey.hex")
python3 part3/lesson-27/verify_commitment.py "$SPK" "$LEAF" "$CTRL"
$CLI -rpcwallet=miner -generate 1 > /dev/null
