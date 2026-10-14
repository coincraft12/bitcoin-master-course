#!/usr/bin/env bash
# 5-2 LAB ① (s52-lab1) T-03: SegWit 송금 하나 만들고 raw hex 저장. 저장소 최상위에서 실행.
#   bash part3/lesson-20/t03_segwit.sh        → ./t03_segwit.hex (다음 단계 verify_with_core.py가 읽는다)
set -euo pipefail
# miner → alice 0.3 BTC (bech32)
TXID=$(bitcoin-cli -regtest -rpcwallet=miner sendtoaddress \
  "$(bitcoin-cli -regtest -rpcwallet=alice getnewaddress "" bech32)" 0.3)
echo "TXID=$TXID"
# 출력된 txid로 hex 받기 (미확정이라 txindex 없이도 조회)
bitcoin-cli -regtest getrawtransaction "$TXID" > t03_segwit.hex
echo "저장: t03_segwit.hex ($(wc -c < t03_segwit.hex) 글자)"
