#!/usr/bin/env bash
# 11-2 실습: regtest는 150블록마다 반감 (s112-lab2). 저장소 최상위에서 실행.
#   bash part4/lesson-45/regtest_halving.sh
# 필요: regtest 노드, miner 지갑, jq. 블록을 많이 만든 뒤에는 env/reset_regtest.sh로 되돌려도 된다.
set -euo pipefail
CLI="bitcoin-cli -regtest"
H=$($CLI getblockcount)
[ $H -lt 310 ] && $CLI generatetoaddress $((310 - H)) $($CLI -rpcwallet=miner getnewaddress) >/dev/null
for h in 149 150 299 300; do
  echo "$h: $($CLI getblockstats $h '["subsidy"]' | jq .subsidy)"
done
echo "# subsidy(h, interval=150)과 일치 확인"
python3 part4/lesson-45/subsidy.py | tail -4
