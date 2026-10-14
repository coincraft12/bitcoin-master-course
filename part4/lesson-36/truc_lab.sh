#!/usr/bin/env bash
# 8-5 실습 ①②③: version 3 부모, 자식 두 개 시도, v2 비교 (s85-lab1, s85-lab2).
# 저장소 최상위에서 실행: bash part4/lesson-36/truc_lab.sh
# 필요: regtest 노드(Core 28 이상, 슬라이드 실측은 31.1), miner·alice·bob 지갑, jq.
set -uo pipefail       # 거부 메시지를 관찰해야 하므로 -e는 쓰지 않는다
CLI="bitcoin-cli -regtest"

echo "######## ① version 3 부모 ########"
BOB=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
RAW=$(bitcoin-cli -regtest createrawtransaction '[]' "[{\"$BOB\":0.1}]")
FUNDED=$(bitcoin-cli -regtest -rpcwallet=alice fundrawtransaction $RAW '{"fee_rate":2}' | jq -r .hex)
V3="03000000${FUNDED:8}"                 # 앞 4바이트(version)를 3으로
SIGNED=$(bitcoin-cli -regtest -rpcwallet=alice signrawtransactionwithwallet $V3 | jq -r .hex)
bitcoin-cli -regtest decoderawtransaction $SIGNED | jq .version   # 3
PARENT=$(bitcoin-cli -regtest sendrawtransaction $SIGNED)
echo "PARENT=$PARENT"

# 자식 하나 만들기: $1 지갑, $2 부모 txid, $3 vout, $4 그 출력 금액(BTC), $5 수수료율(sat/vB), $6 version
# 입력 1·출력 1 P2WPKH 자식(110 vB)으로 보고 수수료 = 수수료율 × 110 sat.
# 지갑 send에는 version 지정이 없을 수 있어 부모와 같은 방식(앞 4바이트 교체)으로 만든다.
child() {
  local DEST AMT RAWC HEX
  DEST=$($CLI -rpcwallet="$1" getnewaddress)
  AMT=$(python3 -c "from decimal import Decimal as D; print(D('$4') - D($5 * 110) / D(10**8))")
  RAWC=$($CLI createrawtransaction "[{\"txid\":\"$2\",\"vout\":$3}]" "[{\"$DEST\":$AMT}]")
  [ "$6" = 3 ] && RAWC="03000000${RAWC:8}"
  HEX=$($CLI -rpcwallet="$1" signrawtransactionwithwallet "$RAWC" | jq -r .hex)
  $CLI sendrawtransaction "$HEX"
}
outputs() {   # 부모의 bob 출력과 잔돈 출력 → "BOB_VOUT BOB_VALUE CHG_VOUT CHG_VALUE"
  $CLI getrawtransaction "$1" true | jq -r --arg a "$2" \
    '[(.vout[] | select(.scriptPubKey.address==$a) | .n, .value), (.vout[] | select(.scriptPubKey.address!=$a) | .n, .value)] | @tsv'
}

read -r BV BVAL CV CVAL <<<"$(outputs "$PARENT" "$BOB")"
echo "######## ②-A 첫 번째 v3 자식: 부모의 bob 출력 (bob 지갑, 10 sat/vB) ########"
A=$(child bob "$PARENT" "$BV" "$BVAL" 10 3) && echo "수락 A=$A"
echo "######## ②-B 두 번째 v3 자식: 부모의 잔돈 출력 (alice 지갑) ########"
echo "-- 5 sat/vB (첫 자식보다 절대 수수료가 작다)"
child alice "$PARENT" "$CV" "$CVAL" 5 3 && echo "(예상과 다름: 수락됨)"
echo "-- 50 sat/vB (첫 자식보다 절대 수수료가 크다 → 형제 축출)"
B=$(child alice "$PARENT" "$CV" "$CVAL" 50 3) && echo "수락 B=$B"
echo "A가 멤풀에 있나: $($CLI getrawmempool | jq --arg t "${A:-x}" 'index($t) != null')"
echo "B가 멤풀에 있나: $($CLI getrawmempool | jq --arg t "${B:-x}" 'index($t) != null')"
echo "부모의 자손: $($CLI getmempoolentry "$PARENT" | jq -c .spentby)"
echo "(선택) Core 31 클러스터 보기:"
$CLI getmempoolcluster "$PARENT" 2>/dev/null | jq -c . || echo "  bitcoin-cli help getmempoolcluster 로 인자를 확인한다"

echo "######## ③ 같은 실험을 v2로 ########"
BOB=$($CLI -rpcwallet=bob getnewaddress)
RAW=$($CLI createrawtransaction '[]' "[{\"$BOB\":0.1}]")
FUNDED=$($CLI -rpcwallet=alice fundrawtransaction "$RAW" '{"fee_rate":2}' | jq -r .hex)
SIGNED=$($CLI -rpcwallet=alice signrawtransactionwithwallet "$FUNDED" | jq -r .hex)
echo "version: $($CLI decoderawtransaction "$SIGNED" | jq .version)"
PARENT2=$($CLI sendrawtransaction "$SIGNED")
read -r BV BVAL CV CVAL <<<"$(outputs "$PARENT2" "$BOB")"
A2=$(child bob "$PARENT2" "$BV" "$BVAL" 10 2) && echo "수락 A2=$A2"
B2=$(child alice "$PARENT2" "$CV" "$CVAL" 5 2) && echo "수락 B2=$B2"
echo "v2 부모의 자손 수: $($CLI getmempoolentry "$PARENT2" | jq '.spentby | length')"

$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "블록 1개로 정리 완료"
