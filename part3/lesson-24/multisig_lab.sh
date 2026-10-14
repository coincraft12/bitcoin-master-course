#!/usr/bin/env bash
# 6-2 LAB ①~⑤ (s62-lab1, lab2, lab2b, lab3): xpub 셋 → 2-of-3 디스크립터 → 감시 지갑 입금 → 서명 둘·결합·전파 → witness 해부.
# 저장소 최상위에서 실행. Bitcoin Core 공식 멀티시그 튜토리얼과 같은 흐름.
#   bash part3/lesson-24/multisig_lab.sh
# xpub_1.txt ~ xpub_3.txt는 6-5(lesson-27)에서 다시 쓰므로 지우지 말 것.
set -euo pipefail
CLI="bitcoin-cli -regtest"

# 1. 참여자 지갑 3개, 키 출처 포함 tpub 추출
for n in 1 2 3; do $CLI createwallet participant_$n > /dev/null 2>&1 || $CLI loadwallet participant_$n > /dev/null 2>&1 || true; done
for n in 1 2 3; do
  $CLI -rpcwallet=participant_$n listdescriptors \
    | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == false) | .desc' \
    | grep -o '\[.*\][a-zA-Z0-9]*' > xpub_$n.txt
done
cat xpub_1.txt xpub_2.txt xpub_3.txt
# 2. 2-of-3 디스크립터 (받는용 /0/*, 잔돈용 /1/*)
X1=$(cat xpub_1.txt); X2=$(cat xpub_2.txt); X3=$(cat xpub_3.txt)
EXT="wsh(sortedmulti(2,$X1/0/*,$X2/0/*,$X3/0/*))"
INT="wsh(sortedmulti(2,$X1/1/*,$X2/1/*,$X3/1/*))"
EXT="$EXT#$($CLI getdescriptorinfo "$EXT" | jq -r .checksum)"
INT="$INT#$($CLI getdescriptorinfo "$INT" | jq -r .checksum)"
echo "EXT=$EXT"; echo "INT=$INT"

# 3. 키 없는 감시 지갑 + 입금
$CLI -named createwallet wallet_name=multisig \
  disable_private_keys=true blank=true > /dev/null 2>&1 || $CLI loadwallet multisig > /dev/null 2>&1 || true
$CLI -rpcwallet=multisig importdescriptors "[
  {\"desc\":\"$EXT\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$INT\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c '[.[].success]'
MS_ADDR=$($CLI -rpcwallet=multisig getnewaddress)
echo "MS_ADDR=$MS_ADDR"
$CLI -rpcwallet=miner sendtoaddress "$MS_ADDR" 2 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null

# 4. PSBT → participant_1, _3 서명 → Combiner → 전파
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)      # 5강의 bob 지갑 bech32 주소
PSBT=$($CLI -rpcwallet=multisig walletcreatefundedpsbt \
  '[]' "[{\"$BOB\":0.5}]" 0 '{"fee_rate":5}' | jq -r .psbt)
P1=$($CLI -rpcwallet=participant_1 walletprocesspsbt "$PSBT" | jq -r .psbt)
P3=$($CLI -rpcwallet=participant_3 walletprocesspsbt "$PSBT" | jq -r .psbt)
$CLI analyzepsbt "$P1" | jq -c '{next}'          # 아직 서명 부족
COMBINED=$($CLI combinepsbt "[\"$P1\",\"$P3\"]")
HEX=$($CLI finalizepsbt "$COMBINED" | jq -r .hex)
$CLI sendrawtransaction "$HEX"

# 5. witness 해부: [0] 빈 값(NULLDUMMY) [1][2] 서명 [3] witness script
$CLI decoderawtransaction "$HEX" | jq '.vin[0].txinwitness'
WS=$($CLI decoderawtransaction "$HEX" | jq -r '.vin[0].txinwitness[3]')
$CLI decodescript "$WS" | jq -r .asm
$CLI -rpcwallet=miner -generate 1 > /dev/null
