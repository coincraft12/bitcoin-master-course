#!/usr/bin/env bash
# 10-2 실습: 포함 증명 (s102-lab 오른쪽 아래). 저장소 최상위에서 실행.
#   bash part4/lesson-41/proof_lab.sh
# 필요: regtest 노드(txindex=1, 2-1), miner·alice·bob 지갑, jq.
set -euo pipefail
TXID=$(bitcoin-cli -regtest -rpcwallet=alice sendtoaddress "$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)" 0.01)
bitcoin-cli -regtest -rpcwallet=miner -generate 1 >/dev/null
echo "TXID=$TXID"
PROOF=$(bitcoin-cli -regtest gettxoutproof "[\"$TXID\"]")
bitcoin-cli -regtest verifytxoutproof $PROOF      # txid가 돌아오면 유효
echo "# PROOF 앞 80바이트 = 블록 헤더 (10-1 파서로) · 형제 해시를 꺼내 루트 재계산"
python3 part4/lesson-41/txoutproof.py "$PROOF"
