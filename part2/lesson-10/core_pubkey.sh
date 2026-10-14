#!/usr/bin/env bash
# 3-2 실습: Core legacy 주소의 공개키를 꺼내 y를 복원한다. 저장소 최상위에서 실행.
#   bash part2/lesson-10/core_pubkey.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"
ADDR=$($CLI -rpcwallet=alice getnewaddress "" legacy)
PUB=$($CLI -rpcwallet=alice getaddressinfo "$ADDR" | jq -r .pubkey)
echo "주소   : $ADDR"
echo "pubkey : $PUB"
python3 part2/lesson-10/parse_core_pubkey.py "$PUB"
