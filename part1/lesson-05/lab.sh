#!/usr/bin/env bash
# 2-1 LAB 4~5단계: regtest로 실행하고 응답 확인, 종료했다가 다시 실행
# 준비: 배포본 검증·설치(1~2단계), 데이터 디렉터리에 bitcoin.conf 두기(3단계) — env/README.md
# 실행: part1/lesson-05/lab.sh
set -e

# 노드가 RPC에 응답할 때까지 기다린다(실행 직후에는 준비 중 오류가 난다)
wait_ready() {
  until bitcoin-cli -regtest getblockchaininfo >/dev/null 2>&1; do sleep 1; done
}
# 노드가 완전히 내려갈 때까지 기다린다
wait_stopped() {
  while bitcoin-cli -regtest getblockchaininfo >/dev/null 2>&1; do sleep 1; done
  sleep 2
}

# 4단계: regtest로 실행하고 응답 확인
bitcoind -regtest -daemon
wait_ready
bitcoin-cli -regtest \
  getblockchaininfo

# 5단계: 종료했다가 다시 실행해 보기
bitcoin-cli -regtest stop
wait_stopped
bitcoind -regtest -daemon
wait_ready
bitcoin-cli -regtest getblockchaininfo | jq '{chain, blocks}'
