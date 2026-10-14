#!/usr/bin/env bash
# 5강 미니 과제 01 정답 예: 레거시(P2PKH)·SegWit(P2WPKH)·Taproot(P2TR) 주소로 받은 코인을 같은 구성으로 하나씩 지출.
# 저장소 최상위에서 실행 (3-5 measure_sizes.sh와 같은 방식, 유형 셋만).
#   bash part3/lesson-22/assignment/solution/send_three.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"
OUT=t05; mkdir -p "$OUT"
declare -A ADDR
for T in legacy bech32 bech32m; do
  ADDR[$T]=$($CLI -rpcwallet=alice getnewaddress "" $T)
  $CLI -rpcwallet=miner sendtoaddress "${ADDR[$T]}" 0.1 > /dev/null
done
$CLI -rpcwallet=miner -generate 1 > /dev/null
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
for T in legacy bech32 bech32m; do
  U=$($CLI -rpcwallet=alice listunspent 1 9999999 "[\"${ADDR[$T]}\"]" | jq -c '.[0] | {txid, vout}')
  TXID=$($CLI -rpcwallet=alice send "{\"$BOB\":0.09}" null "unset" 5 \
    "{\"inputs\":[$U],\"add_inputs\":false,\"change_type\":\"bech32\"}" | jq -r .txid)
  $CLI -rpcwallet=alice gettransaction "$TXID" | jq -r .hex > "$OUT/spend_$T.hex"
done
$CLI -rpcwallet=miner -generate 1 > /dev/null
python3 part3/lesson-22/assignment/solution/solution_compare.py --node \
  "$OUT/spend_legacy.hex" "$OUT/spend_bech32.hex" "$OUT/spend_bech32m.hex"
