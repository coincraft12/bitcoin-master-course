#!/usr/bin/env bash
# 3-5 실습 T-03: 유형별 지출 크기 측정 (s35-lab, s35-result). 저장소 최상위에서 실행.
#   bash part2/lesson-13/measure_sizes.sh
# 네 유형(legacy, p2sh-segwit, bech32, bech32m) 주소로 0.1 BTC씩 받은 뒤, 유형마다 그 UTXO 하나만
# 써서 bob에게 0.09 BTC를 보낸다(잔돈은 bech32 고정, 5 sat/vB). 지출 트랜잭션 hex는
# data/T-03/spend_<유형>.hex 로 저장해 5강 실습에서 재사용한다.
set -euo pipefail
CLI="bitcoin-cli -regtest"
OUTDIR=data/T-03
mkdir -p "$OUTDIR"

# 1. 네 유형의 주소로 0.1 BTC씩 받기
declare -A ADDR
for T in legacy p2sh-segwit bech32 bech32m; do
  A=$($CLI -rpcwallet=alice getnewaddress "" $T)
  $CLI -rpcwallet=miner sendtoaddress "$A" 0.1 > /dev/null; echo "$T $A"
  ADDR[$T]=$A
done
$CLI -rpcwallet=miner -generate 1 > /dev/null

# 2. 유형마다 그 UTXO 하나만 써서 bob에게 0.09 BTC · 잔돈은 bech32로 고정
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
printf "\n%-12s %10s %8s %18s\n" "입력 유형" "vsize(vB)" "weight" "5 sat/vB 수수료(sat)"
for T in legacy p2sh-segwit bech32 bech32m; do
  U=$($CLI -rpcwallet=alice listunspent 1 9999999 "[\"${ADDR[$T]}\"]" | jq -c '.[0] | {txid, vout}')
  TXID=$($CLI -rpcwallet=alice send "{\"$BOB\":0.09}" null "unset" 5 \
    "{\"inputs\":[$U],\"add_inputs\":false,\"change_type\":\"bech32\"}" | jq -r .txid)
  D=$($CLI -rpcwallet=alice gettransaction "$TXID" false true)
  VSIZE=$(echo "$D" | jq '.decoded.vsize'); WEIGHT=$(echo "$D" | jq '.decoded.weight')
  echo "$D" | jq -r .hex > "$OUTDIR/spend_$T.hex"
  printf "%-12s %10s %8s %18s\n" "$T" "$VSIZE" "$WEIGHT" "$((VSIZE * 5))"
done
$CLI -rpcwallet=miner -generate 1 > /dev/null
echo; echo "저장: $OUTDIR/spend_{legacy,p2sh-segwit,bech32,bech32m}.hex"
