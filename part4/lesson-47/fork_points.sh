#!/usr/bin/env bash
# 11-4 실습 보조: 분리 지점과 SegWit 활성 블록을 내 메인넷 노드로 확인 (s114-lab의 01·04).
# 탐색기로 하는 실습이라 노드가 없어도 된다. 메인넷 풀노드(가지치기하지 않은)가 있을 때만 실행.
#   bash part4/lesson-47/fork_points.sh
set -euo pipefail
CLI="bitcoin-cli"
if ! $CLI getblockchaininfo >/dev/null 2>&1; then
  echo "메인넷 노드가 없다 → 탐색기로 진행 (README의 실습 순서)"; exit 0
fi
echo "# 01 비트코인 블록 478,558 · 478,559 (비트코인캐시 탐색기의 같은 높이와 비교)"
for h in 478558 478559; do
  echo "$h $($CLI getblockhash $h)"
done
echo "# 04 블록 481,824 전후: witness가 있는 트랜잭션 수 (SegwitHeight = 481824, Core chainparams.cpp)"
for h in 481823 481824 481825; do
  B=$($CLI getblock "$($CLI getblockhash $h)" 2)
  echo "$h 트랜잭션 $(echo "$B" | jq '.tx | length')개, witness 있는 것 $(echo "$B" | jq '[.tx[] | select(any(.vin[]; has("txinwitness")))] | length')개"
done
echo "# Core가 기억하는 SegWit 활성 높이"
$CLI getdeploymentinfo | jq '.deployments.segwit | {type, active, height}'
