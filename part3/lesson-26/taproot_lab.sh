#!/usr/bin/env bash
# 6-4 LAB ①~④ (s64-lab1~3): Core에서 내부키·출력키 얻기 → 코드로 재현 → 키 경로 지출 관찰. 저장소 최상위에서 실행.
#   bash part3/lesson-26/taproot_lab.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"

# ① P와 Q
TR=$($CLI -rpcwallet=alice getnewaddress "" bech32m)
$CLI -rpcwallet=alice getaddressinfo "$TR" | jq '{desc, witness_program}'
P_X=$($CLI -rpcwallet=alice getaddressinfo "$TR" | jq -r .desc | grep -o '\][0-9a-f]\{64\})' | tr -d '])')
# ③ 대조: 출력 첫 줄 = witness_program, 둘째 줄 = $TR
python3 part3/lesson-26/match_wallet.py "$P_X"
echo "TR=$TR"

# ④ 키 경로 지출 관찰
$CLI -rpcwallet=miner sendtoaddress "$TR" 0.5 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null
TXID=$($CLI -rpcwallet=alice send \
  "{\"$($CLI -rpcwallet=bob getnewaddress)\":0.4}" null "unset" 5 | jq -r .txid)
$CLI getrawtransaction "$TXID" true \
  | jq '.vin[] | {txinwitness, len: (.txinwitness | map(length/2))}'
$CLI -rpcwallet=miner -generate 1 > /dev/null
