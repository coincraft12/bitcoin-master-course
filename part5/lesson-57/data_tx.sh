#!/usr/bin/env bash
# 14-1 실습: 데이터 트랜잭션 해부 (s141-lab)
# regtest에서 OP_RETURN 출력을 가진 트랜잭션을 만들고 testmempoolaccept로 내 노드 정책 판정을 본다.
# 준비: env/setup_regtest.sh (alice 지갑). 서명만 하고 전파하지 않는다(testmempoolaccept는 검사만).
#
#   bash part5/lesson-57/data_tx.sh            # 슬라이드 그대로: "CoinCraft Bitcoin Master Course" (31바이트)
#   bash part5/lesson-57/data_tx.sh 80         # 0xab를 80바이트
#   bash part5/lesson-57/data_tx.sh 99000      # 큰 데이터는 bitcoin-cli -stdin으로 넘긴다
#
# -datacarriersize=83 비교: 노드를 그 옵션으로 다시 띄운 뒤 같은 명령을 돌린다 (README 참고).
set -e
CLI="bitcoin-cli -regtest"
$CLI -rpcwallet=alice getwalletinfo >/dev/null 2>&1 || $CLI loadwallet alice >/dev/null

if [ -z "$1" ]; then
  # ---- 슬라이드 명령 그대로 ----
  DATA=$(python3 -c "print(b'CoinCraft Bitcoin Master Course'.hex())")
  RAW=$($CLI createrawtransaction '[]' "[{\"data\":\"$DATA\"}]")
  FUNDED=$($CLI -rpcwallet=alice fundrawtransaction "$RAW" | jq -r .hex)
  SIGNED=$($CLI -rpcwallet=alice signrawtransactionwithwallet "$FUNDED" | jq -r .hex)
  $CLI testmempoolaccept "[\"$SIGNED\"]"
  $CLI decoderawtransaction "$SIGNED" | jq '.vout[] | select(.scriptPubKey.type=="nulldata")'
  exit 0
fi

# ---- 크기를 바꿔 가며 (데이터 N바이트, 모두 0xab) ----
N=$1
[[ "$N" =~ ^[0-9]+$ ]] && [ "$N" -gt 0 ] || { echo "데이터 바이트 수를 양의 정수로 주세요"; exit 1; }
DATA=$(python3 -c "print('ab' * $N)")
# 명령줄 인자 한 개의 길이 제한(리눅스 약 128KB)을 피하려고 모든 큰 값은 -stdin으로 넘긴다.
# printf와 echo는 셸 내장이라 이 제한에 걸리지 않는다. -stdin은 한 줄에 인자 하나.
RAW=$(printf '%s\n%s\n' '[]' "[{\"data\":\"$DATA\"}]" | $CLI -stdin createrawtransaction)
FUNDED=$(echo "$RAW" | $CLI -rpcwallet=alice -stdin fundrawtransaction | jq -r .hex)
SIGNED=$(echo "$FUNDED" | $CLI -rpcwallet=alice -stdin signrawtransactionwithwallet | jq -r .hex)
printf '["%s"]\n' "$SIGNED" | $CLI -stdin testmempoolaccept | jq -c '.[0] | {allowed, vsize, "reject-reason"}'
echo "$SIGNED" | $CLI -stdin decoderawtransaction \
  | jq -c '{vsize, nulldata: [.vout[] | select(.scriptPubKey.type=="nulldata") | {n, script_bytes: (.scriptPubKey.hex | length / 2)}]}'
