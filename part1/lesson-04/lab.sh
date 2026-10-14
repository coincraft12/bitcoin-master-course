#!/usr/bin/env bash
# 1-4 LAB: 잔액을 UTXO로 해체하기 — 2강 이후, 내 노드에서 같은 실습 반복
# 준비: env/setup_regtest.sh 실행 완료(miner·alice·bob), jq 설치
# 실행: 저장소 최상위에서 part1/lesson-04/lab.sh
set -e

# 슬라이드 넷째 줄의 <alice 주소>는 alice가 가진 UTXO의 실제 주소로 채운다
ALICE_ADDR=$(bitcoin-cli -regtest -rpcwallet=alice listunspent | jq -r '.[0].address')

bitcoin-cli -regtest gettxoutsetinfo | jq '{txouts, total_amount}'
bitcoin-cli -regtest -rpcwallet=alice listunspent
bitcoin-cli -regtest -rpcwallet=alice getbalance
bitcoin-cli -regtest scantxoutset start "[\"addr($ALICE_ADDR)\"]"
