#!/usr/bin/env bash
# 8-4 실습 ③(선택): 묶음으로 제출하기 — submitpackage (s84-lab2). 저장소 최상위에서 실행.
#   bash part4/lesson-35/submitpackage_lab.sh restart   # 노드를 -minrelaytxfee=0.00005로 다시 띄우고 지갑 로드
#   bash part4/lesson-35/submitpackage_lab.sh           # 실습
#   bash part4/lesson-35/submitpackage_lab.sh restore   # 기본 설정으로 다시 띄우기
# Core 30부터 최소 릴레이 수수료가 0.1 sat/vB라, 부모가 문턱 아래인 상황을 만들려면 5 sat/vB로 띄운다.
set -euo pipefail
CLI="bitcoin-cli -regtest"

restart_node() {   # $@ = bitcoind 추가 옵션
  if $CLI getblockchaininfo >/dev/null 2>&1; then
    $CLI stop >/dev/null
    while $CLI getblockchaininfo >/dev/null 2>&1; do sleep 1; done
    sleep 1
  fi
  bitcoind -regtest -daemon "$@"
  until $CLI getblockchaininfo >/dev/null 2>&1; do sleep 1; done
  for W in miner alice bob; do
    $CLI -rpcwallet=$W getwalletinfo >/dev/null 2>&1 || $CLI loadwallet $W >/dev/null
  done
  echo "minrelaytxfee = $($CLI getmempoolinfo | jq .minrelaytxfee) BTC/kvB"
}

case "${1:-}" in
  restart) restart_node -minrelaytxfee=0.00005; exit 0 ;;
  restore) restart_node; exit 0 ;;
esac

MIN=$($CLI getmempoolinfo | jq .minrelaytxfee)
if ! python3 -c "import sys; from decimal import Decimal as D; sys.exit(0 if D('$MIN') >= D('0.00005') else 1)"; then
  echo "지금 minrelaytxfee = $MIN BTC/kvB. 먼저: bash part4/lesson-35/submitpackage_lab.sh restart"
  exit 1
fi

BOB=$($CLI -rpcwallet=bob getnewaddress)
BOB2=$($CLI -rpcwallet=bob getnewaddress)
# 노드를 -minrelaytxfee=0.00005(5 sat/vB)로 띄운다 · 부모는 1 sat/vB로 서명만
RAW=$(bitcoin-cli -regtest createrawtransaction '[]' "[{\"$BOB\":0.2}]")
F=$(bitcoin-cli -regtest -rpcwallet=alice fundrawtransaction $RAW '{"fee_rate":1}' | jq -r .hex) || F=""
if [ -z "$F" ]; then
  # (저장소 보완) 지갑이 노드의 최소 수수료보다 낮은 fee_rate를 거부하면, 입력·잔돈을 직접 채워
  # 같은 모양(입력 1·출력 2)의 부모를 만든다. 수수료 141 sat = 141 vB × 1 sat/vB.
  echo "→ 지갑이 fee_rate 1을 거부했다. 입력과 잔돈을 직접 채운다."
  U=$($CLI -rpcwallet=alice listunspent 1 | jq -c 'map(select(.amount >= 0.3)) | .[0]')
  CHG=$($CLI -rpcwallet=alice getrawchangeaddress bech32)
  CHANGE=$(python3 -c "from decimal import Decimal as D; print(D('$(echo "$U" | jq -r .amount)') - D('0.2') - D('0.00000141'))")
  F=$($CLI createrawtransaction "[$(echo "$U" | jq -c '{txid, vout}')]" "[{\"$BOB\":0.2},{\"$CHG\":$CHANGE}]")
fi
PARENT_HEX=$(bitcoin-cli -regtest -rpcwallet=alice signrawtransactionwithwallet $F | jq -r .hex)
bitcoin-cli -regtest testmempoolaccept "[\"$PARENT_HEX\"]"      # min relay fee not met
# 슬라이드의 PID·PV·SPK: 서명한 부모를 디코딩해 bob 출력의 txid, vout, scriptPubKey를 얻는다
DEC=$($CLI decoderawtransaction "$PARENT_HEX")
PID=$(echo "$DEC" | jq -r .txid)
PV=$(echo "$DEC" | jq --arg a "$BOB" '.vout[] | select(.scriptPubKey.address==$a) | .n')
SPK=$(echo "$DEC" | jq -r --arg a "$BOB" '.vout[] | select(.scriptPubKey.address==$a) | .scriptPubKey.hex')
echo "PID=$PID PV=$PV SPK=$SPK"
# 자식: 부모의 bob 출력을 쓰고 수수료를 넉넉히 (prevtxs로 미전파 부모 정보 전달)
CRAW=$(bitcoin-cli -regtest createrawtransaction \
  "[{\"txid\":\"$PID\",\"vout\":$PV}]" "[{\"$BOB2\":0.1997}]")
CHILD_HEX=$(bitcoin-cli -regtest -rpcwallet=bob signrawtransactionwithwallet $CRAW \
  "[{\"txid\":\"$PID\",\"vout\":$PV,\"scriptPubKey\":\"$SPK\",\"amount\":0.2}]" | jq -r .hex)
bitcoin-cli -regtest submitpackage "[\"$PARENT_HEX\",\"$CHILD_HEX\"]"
echo "멤풀 건수: $($CLI getrawmempool | jq length)"
echo "# 실습이 끝나면: bash part4/lesson-35/submitpackage_lab.sh restore"
