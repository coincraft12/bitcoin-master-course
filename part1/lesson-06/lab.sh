#!/usr/bin/env bash
# 2-2 LAB: 성숙 규칙을 손으로 확인하기
# 준비: bitcoind -regtest -daemon 실행 중. 처음 상태에서 하는 것이 좋다(env/reset_regtest.sh).
# 실행: 저장소 최상위에서 part1/lesson-06/lab.sh
# 슬라이드처럼 한 줄씩 터미널에 직접 쳐 보는 것을 권한다.

# 스크립트 전에 손으로 먼저
CLI="bitcoin-cli -regtest"; $CLI createwallet test
A=$($CLI -rpcwallet=test getnewaddress)
$CLI generatetoaddress 1 $A;   $CLI -rpcwallet=test getbalances   # immature 50
$CLI generatetoaddress 100 $A; $CLI -rpcwallet=test getbalance    # 50.00000000
