#!/usr/bin/env bash
# 11-5 실습 ②: regtest에서 활성화 재현 (s115-lab2). 저장소 최상위에서 실행.
#   bash env/reset_regtest.sh          # 먼저 초기화 (이미 활성 상태일 수 있다 — 많이 막히는 곳)
#   bash part4/lesson-48/testdummy_lab.sh
# 노드가 없으면 띄우고 miner 지갑이 없으면 만든다. 시작 높이가 144 이상이면 초기화를 안내하고 멈춘다.
set -euo pipefail

# (저장소 보탬) 준비
bitcoin-cli -regtest getblockchaininfo >/dev/null 2>&1 || bitcoind -regtest -daemon
until bitcoin-cli -regtest getblockchaininfo >/dev/null 2>&1; do sleep 1; done
bitcoin-cli -regtest -rpcwallet=miner getwalletinfo >/dev/null 2>&1 \
  || bitcoin-cli -regtest loadwallet miner >/dev/null 2>&1 \
  || bitcoin-cli -regtest createwallet miner >/dev/null
START=$(bitcoin-cli -regtest getblockcount)
if [ "$START" -ge 144 ]; then
  echo "지금 높이 $START — testdummy가 이미 진행됐다. bash env/reset_regtest.sh 후 다시 실행한다."
  exit 1
fi
echo "시작 높이 $START"

# 새 regtest에서 시작 (2-2 reset) · testdummy: bit 28, 구간 144, 임계치 108(75%)
CLI="bitcoin-cli -regtest"
ADDR=$($CLI -rpcwallet=miner getnewaddress)
for i in 1 2 3; do
  $CLI generatetoaddress 144 $ADDR >/dev/null
  $CLI getdeploymentinfo | jq -c '.deployments.testdummy.bip9 | {status, since}'
done

echo "# 블록 version을 10-1 파서로: 신호 구간 0x30000000 → 활성 후 0x20000000"
python3 part4/lesson-48/header_versions.py 143 144 287 288 431 432
echo "# 같은 결과를 노드 없이 계산: python3 part4/lesson-48/bip9_sim.py $START"
