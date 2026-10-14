#!/usr/bin/env bash
# 8-1 실습: 수수료 계산과 추정 비교 (s81-lab). 저장소 최상위에서 실행.
#   bash part4/lesson-32/fee_lab.sh
# 필요: regtest 노드, miner·alice·bob 지갑(env/setup_regtest.sh), jq.
# 메인넷 노드가 같은 컴퓨터에서 돌고 있으면 2단계 estimatesmartfee 비교도 한다.
set -euo pipefail

echo "# 1단계: mempool.space 첫 화면에서 '다음 블록·30분·1시간' 추천 수수료율을 활동지에 기록한다 (브라우저)."

echo "# 2단계: estimatesmartfee 1·6·144"
if bitcoin-cli getblockchaininfo >/dev/null 2>&1; then
  for N in 1 6 144; do
    echo "메인넷 $N블록 목표: $(bitcoin-cli estimatesmartfee $N | jq -c .)"
  done
else
  echo "메인넷 노드 없음 → 건너뜀"
fi
echo "regtest는 수수료 시장 데이터가 없어 데이터 부족(errors)을 돌려준다 → 2-1에서 fallbackfee를 둔 이유:"
bitcoin-cli -regtest estimatesmartfee 6 | jq -c .

echo "# 3단계: alice → bob 0.1 BTC, fee_rate 5 sat/vB"
TXID=$(bitcoin-cli -regtest -rpcwallet=alice -named sendtoaddress \
  address=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress) amount=0.1 fee_rate=5)
bitcoin-cli -regtest -rpcwallet=alice gettransaction $TXID true | jq '{fee, vsize: .decoded.vsize}'
# fee는 BTC 단위 음수 → sat로 바꿔 5 × vsize와 비교
python3 part4/lesson-32/fee_calc.py --check \
  "$(bitcoin-cli -regtest -rpcwallet=alice gettransaction $TXID true | jq -c '{fee, vsize: .decoded.vsize}')" 5 || true

echo "# 마무리: 3-5(T-03)에서 저장한 유형별 지출로 같은 금액 송금의 수수료 차이 (5 sat/vB)"
if ls data/T-03/spend_*.hex >/dev/null 2>&1; then
  printf "%-12s %8s %16s\n" "입력 유형" "vsize" "5 sat/vB 수수료"
  for T in legacy p2sh-segwit bech32 bech32m; do
    F=data/T-03/spend_$T.hex
    [ -f "$F" ] || continue
    V=$(bitcoin-cli -regtest decoderawtransaction "$(cat "$F")" | jq .vsize)
    printf "%-12s %8s %16s\n" "$T" "$V" "$((V * 5)) sat"
  done
else
  echo "data/T-03/ 가 없다 → 먼저 bash part2/lesson-13/measure_sizes.sh"
fi
bitcoin-cli -regtest -rpcwallet=miner -generate 1 >/dev/null
