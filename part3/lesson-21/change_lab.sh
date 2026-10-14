#!/usr/bin/env bash
# 5-3 LAB ①②③ (s53-lab1~3): 잔돈을 일부러 빼먹기 → 잔돈 넣기 → Core에 맡기기. 저장소 최상위에서 실행.
#   bash part3/lesson-21/change_lab.sh
# 준비물: 5-2 t03_segwit.sh로 alice가 받은 0.3 BTC 코인 (아직 안 썼어야 한다)
set -euo pipefail
CLI="bitcoin-cli -regtest"

# 준비: 5-2의 0.3 BTC 확정 → TXID·VOUT 확인
$CLI -rpcwallet=miner -generate 1 > /dev/null
$CLI -rpcwallet=alice listunspent | jq -c '.[] | {txid, vout, amount}'
U=$($CLI -rpcwallet=alice listunspent | jq -c 'map(select(.amount == 0.3)) | .[0]')
if [ "$U" = "null" ]; then echo "0.3 BTC 코인이 없습니다. 먼저 part3/lesson-20/t03_segwit.sh를 실행하세요."; exit 1; fi
TXID=$(echo "$U" | jq -r .txid); VOUT=$(echo "$U" | jq -r .vout)
echo "TXID=$TXID VOUT=$VOUT"
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
CHANGE=$($CLI -rpcwallet=alice getrawchangeaddress bech32)

echo "== 1단계: 출력 하나뿐 (0.2 BTC가 수수료로) =="
RAW=$($CLI createrawtransaction \
  '[{"txid":"'"$TXID"'","vout":'"$VOUT"'}]' "[{\"$BOB\":0.1}]")
SIGNED=$($CLI -rpcwallet=alice signrawtransactionwithwallet "$RAW" | jq -r .hex)
$CLI sendrawtransaction "$SIGNED" || echo "→ 기대한 거부: 수수료가 maxfeerate(기본 0.10 BTC/kvB)를 넘음"
$CLI testmempoolaccept "[\"$SIGNED\"]" | jq -c '.[0] | {allowed, "reject-reason"}'

echo "== 2단계: 잔돈을 넣은 송금 =="
RAW=$($CLI createrawtransaction \
  '[{"txid":"'"$TXID"'","vout":'"$VOUT"'}]' \
  "[{\"$BOB\":0.1},{\"$CHANGE\":0.1999}]")
SIGNED=$($CLI -rpcwallet=alice signrawtransactionwithwallet "$RAW" | jq -r .hex)
$CLI decoderawtransaction "$SIGNED" | jq -c '{vsize, vout: [.vout[].value]}'
echo "$SIGNED" > change_tx.hex
$CLI sendrawtransaction "$SIGNED"
python3 part3/lesson-21/fee_check.py change_tx.hex 30000000      # 5-2 파서로 vsize·수수료율 확인

echo "== 3단계: Core에 맡기기 (두 번 실행해 changepos 비교) =="
for _ in 1 2; do
  RAW=$($CLI createrawtransaction '[]' "[{\"$BOB\":0.05}]")
  $CLI -rpcwallet=alice fundrawtransaction "$RAW" '{"fee_rate":10}' | jq -c '{fee, changepos}'
done
$CLI -rpcwallet=miner -generate 1 > /dev/null
