#!/usr/bin/env bash
# 3-3 실습 4단계: Core와 대조. 저장소 최상위에서 실행.
#   bash part2/lesson-11/core_legacy.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"
ADDR=$($CLI -rpcwallet=alice getnewaddress "" legacy)
PUB=$($CLI -rpcwallet=alice getaddressinfo "$ADDR" | jq -r .pubkey)
OUT=$(python3 part2/lesson-11/check_core_legacy.py "$PUB" "$ADDR")
echo "$OUT" | sed '$d'
TYPO=$(echo "$OUT" | tail -n 1)
echo "Core validateaddress(오타):"
$CLI validateaddress "$TYPO" | jq '{isvalid, error}'
