#!/usr/bin/env bash
# 과정 표준 regtest 환경을 만든다 (2-2).
#   노드: bitcoind -regtest 실행 중
#   지갑: miner(채굴·자금 공급), alice(5 BTC), bob(5 BTC)
# 여러 번 실행해도 안전하다. 단, 송금 부분은 매번 다시 돌므로
# 실행할 때마다 alice와 bob의 잔액이 5 BTC씩 늘어나는 것은 정상이다.
# 데이터 디렉터리는 운영체제 기본 위치를 쓴다(2-1).

# 1. 노드 실행, 지갑 3개
set -e
CLI="bitcoin-cli -regtest"
# (저장소 보완) 이미 실행 중이면 다시 띄우지 않는다. ERRATA.md 참고
$CLI getblockchaininfo >/dev/null 2>&1 || bitcoind -regtest -daemon
until $CLI getblockchaininfo \
  >/dev/null 2>&1; do sleep 1; done
for W in miner alice bob; do
  # (저장소 보완) 이미 로드된 지갑은 건너뛴다. ERRATA.md 참고
  $CLI -rpcwallet=$W getwalletinfo >/dev/null 2>&1 && continue
  $CLI loadwallet $W >/dev/null 2>&1 \
  || $CLI createwallet $W >/dev/null
done

# 2. 101블록 채굴, 자금 지급
if [ "$($CLI getblockcount)" -lt 101 ]; then
  $CLI generatetoaddress 101 \
  "$($CLI -rpcwallet=miner getnewaddress)"
fi
# (저장소 보완) 블록은 101개 이상인데 miner의 쓸 수 있는 잔액이 모자라면
# (예: 2-2 LAB에서 test 지갑으로 먼저 101블록을 만든 경우) miner에게 더 채굴한다.
# ERRATA.md 참고
for _ in 1 2 3 4 5; do
  BAL=$($CLI -rpcwallet=miner getbalance)
  [ "${BAL%%.*}" -ge 11 ] && break
  $CLI generatetoaddress 101 \
  "$($CLI -rpcwallet=miner getnewaddress)" >/dev/null
done
for W in alice bob; do
  $CLI -rpcwallet=miner sendtoaddress \
  "$($CLI -rpcwallet=$W getnewaddress)" 5
done
$CLI -rpcwallet=miner -generate 1

# 3. 세 지갑 잔액 출력
echo "---- 지갑 잔액 (블록 높이 $($CLI getblockcount)) ----"
for W in miner alice bob; do
  echo "$W: $($CLI -rpcwallet=$W getbalance) BTC"
done
