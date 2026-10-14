#!/usr/bin/env bash
# 5-1 실습 ①② (s51-lab1, s51-lab2): 블록 170의 첫 P2P 송금을 열고 입력을 거슬러 올라가기. 저장소 최상위에서 실행.
#   bash part3/lesson-19/block170_lab.sh            # 노드가 regtest뿐일 때: 저장소 hex를 decoderawtransaction
#   bash part3/lesson-19/block170_lab.sh mainnet    # txindex=1 메인넷 노드가 있을 때: getrawtransaction
set -euo pipefail

if [ "${1:-}" = "mainnet" ]; then
  # ① 첫 P2P 송금 (블록 170)
  bitcoin-cli getrawtransaction \
    f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16 true
  # ② 입력이 가리키는 이전 트랜잭션 (블록 9의 코인베이스)
  bitcoin-cli getrawtransaction \
    0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9 true
else
  # 노드가 없으면 저장소 hex 사용 (decoderawtransaction은 체인과 무관해 regtest에서도 같은 결과)
  echo "== ① data/T-02.hex (블록 170) =="
  bitcoin-cli -regtest decoderawtransaction "$(cat data/T-02.hex)" \
    | jq '{txid, vin: [.vin[] | {txid, vout}], vout: [.vout[] | {value, type: .scriptPubKey.type}]}'
  echo "== ② data/T-02_prev.hex (블록 9 코인베이스) =="
  bitcoin-cli -regtest decoderawtransaction "$(cat data/T-02_prev.hex)" \
    | jq '{txid, vin: [.vin[] | {coinbase}], vout: [.vout[] | {n, value}]}'
fi
