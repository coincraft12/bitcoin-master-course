#!/usr/bin/env bash
# 3-4 실습: Core bech32 주소와 대조. 저장소 최상위에서 실행.
#   bash part2/lesson-12/core_bech32.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"
ADDR=$($CLI -rpcwallet=alice getnewaddress "" bech32)
INFO=$($CLI -rpcwallet=alice getaddressinfo "$ADDR")
echo "$INFO" | jq '{pubkey, witness_version, witness_program}'
python3 part2/lesson-12/check_core_bech32.py \
  "$(echo "$INFO" | jq -r .pubkey)" "$ADDR" "$(echo "$INFO" | jq -r .witness_program)"
echo "Core p2sh-segwit 주소 (2로 시작):"
$CLI -rpcwallet=alice getnewaddress "" p2sh-segwit
echo "오류 실험 (validateaddress):"
UPPER=$(echo "$ADDR" | tr '[:lower:]' '[:upper:]')
MIXED="${ADDR:0:10}$(echo "${ADDR:10}" | tr '[:lower:]' '[:upper:]')"
LAST=${ADDR: -1}; if [ "$LAST" = "q" ]; then NEW=p; else NEW=q; fi
ONE="${ADDR:0:${#ADDR}-1}$NEW"
for A in "$ONE" "$MIXED" "$UPPER"; do
  echo "$A"; $CLI validateaddress "$A" | jq -c '{isvalid, error}'
done
