#!/usr/bin/env bash
# 1-3 LAB의 regtest 버전: 트랜잭션 하나의 일생을 내 노드에서 따라가기
# 슬라이드 실습은 공개 탐색기로 한다. 2강에서 표준 환경을 만든 뒤 같은 흐름을 내 노드에서 반복한다.
# 준비: env/setup_regtest.sh 실행 완료(miner·alice·bob), jq 설치
# 실행: 저장소 최상위에서 part1/lesson-03/lab.sh
set -e
CLI="bitcoin-cli -regtest"

# 1~3단계 만들기·서명·전파: alice 지갑이 코인을 고르고, 서명하고, 노드에 넘긴다
BOB=$($CLI -rpcwallet=bob getnewaddress)
TXID=$($CLI -rpcwallet=alice sendtoaddress "$BOB" 0.1)
echo "[만들기·서명·전파] txid: $TXID"
$CLI getrawtransaction "$TXID" true | jq '{vin_count: (.vin | length), vout_count: (.vout | length), vsize}'

# 4단계 멤풀: 노드의 대기실에 들어갔는지, 수수료율은 얼마인지
echo "[멤풀] 멤풀에 있는가: $($CLI getrawmempool | jq --arg t "$TXID" 'any(.[]; . == $t)')"
$CLI getmempoolentry "$TXID" | jq '{vsize, fee_btc: .fees.base, feerate_sat_per_vb: (.fees.base * 100000000 / .vsize)}'
echo "[멤풀] 확인 수: $($CLI -rpcwallet=alice gettransaction "$TXID" | jq '.confirmations')"

# 5단계 블록 포함: 채굴자(miner)가 블록을 만들면 담긴다. 담긴 블록 자신이 1 확인
$CLI -rpcwallet=miner -generate 1 >/dev/null
$CLI -rpcwallet=alice gettransaction "$TXID" | jq '{confirmations, blockheight, blockhash}'
echo "[블록 포함] 멤풀에 남아 있는가: $($CLI getrawmempool | jq --arg t "$TXID" 'any(.[]; . == $t)')"

# 6단계 확인 누적: 위에 블록이 5개 더 쌓이면 6 확인
$CLI -rpcwallet=miner -generate 5 >/dev/null
echo "[확인 누적] 확인 수: $($CLI -rpcwallet=alice gettransaction "$TXID" | jq '.confirmations')"
