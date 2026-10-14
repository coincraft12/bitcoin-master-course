#!/usr/bin/env bash
# 8-4 실습 ①②: 받는 쪽에서 가속하기 (s84-lab1). 저장소 최상위에서 실행.
#   bash part4/lesson-35/cpfp_lab.sh
# 필요: regtest 노드, miner·alice·bob 지갑(env/setup_regtest.sh), jq.
set -euo pipefail

# 1. 1 sat/vB 부모
BOB=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
P=$(bitcoin-cli -regtest -rpcwallet=alice -named sendtoaddress address=$BOB amount=0.2 fee_rate=1)
# 2. bob이 미확정 코인으로 30 sat/vB 자식
BOB2=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
VOUT=$(bitcoin-cli -regtest getrawtransaction $P true \
  | jq --arg a "$BOB" '.vout[] | select(.scriptPubKey.address==$a) | .n')
C=$(bitcoin-cli -regtest -rpcwallet=bob -named send outputs="{\"$BOB2\":0.199}" fee_rate=30 \
  options="{\"inputs\":[{\"txid\":\"$P\",\"vout\":$VOUT}],\"add_inputs\":false,\"include_unsafe\":true}" | jq -r .txid)
echo "P=$P"; echo "C=$C"
bitcoin-cli -regtest getmempoolentry $P | jq '{fees, depends, spentby}'
bitcoin-cli -regtest getmempoolentry $C | jq '{fees, depends}'

echo "# 손 계산과 대조: 패키지 수수료율 = (부모 + 자식 수수료) ÷ (부모 + 자식 vsize)"
python3 part4/lesson-35/package_feerate.py --mempool "$P" "$C"

echo "# 확정해서 정리"
bitcoin-cli -regtest -rpcwallet=miner -generate 1 >/dev/null
echo "P 확인 수: $(bitcoin-cli -regtest getrawtransaction $P true | jq .confirmations), C 확인 수: $(bitcoin-cli -regtest getrawtransaction $C true | jq .confirmations)"
