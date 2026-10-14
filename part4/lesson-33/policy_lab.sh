#!/usr/bin/env bash
# 8-2 실습 ①②③: 더스트로 정책에 걸려 보고, 그래도 블록에는 넣어 보기 (s82-lab1, s82-lab2).
# 저장소 최상위에서 실행: bash part4/lesson-33/policy_lab.sh
# 필요: regtest 노드, miner·alice·bob 지갑(env/setup_regtest.sh), jq.
set -uo pipefail     # 정책 거부·지갑 거부를 관찰해야 하므로 -e는 쓰지 않는다

# 1. 멤풀 상태 — 각 필드를 앞 장과 대조
bitcoin-cli -regtest getmempoolinfo | jq '{size, bytes, usage, maxmempool, mempoolminfee, minrelaytxfee}'
# 2. 100 sat 출력 → 전파 전에 정책 검사
BOB=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress "" bech32)
RAW=$(bitcoin-cli -regtest createrawtransaction '[]' "[{\"$BOB\":0.000001}]")
FUNDED=$(bitcoin-cli -regtest -rpcwallet=alice fundrawtransaction $RAW | jq -r .hex)
if [ -z "$FUNDED" ]; then
  echo "→ 지갑 단계에서 먼저 거부됐다: 지갑도 정책을 미리 적용한다. 위 오류 메시지를 읽어 보자."
  echo "  (저장소 보완) 다음 단계를 위해 입력·잔돈을 직접 채워 같은 더스트 트랜잭션을 만든다 (수수료 1,000 sat)."
  U=$(bitcoin-cli -regtest -rpcwallet=alice listunspent 1 | jq -c 'map(select(.amount >= 0.001)) | .[0]')
  CHG=$(bitcoin-cli -regtest -rpcwallet=alice getrawchangeaddress bech32)
  CHANGE=$(python3 -c "from decimal import Decimal as D; print(D('$(echo "$U" | jq -r .amount)') - D('0.000001') - D('0.00001'))")
  FUNDED=$(bitcoin-cli -regtest createrawtransaction "[$(echo "$U" | jq -c '{txid, vout}')]" \
    "[{\"$BOB\":0.000001},{\"$CHG\":$CHANGE}]")
fi
SIGNED=$(bitcoin-cli -regtest -rpcwallet=alice signrawtransactionwithwallet $FUNDED | jq -r .hex)
DUST=$SIGNED
bitcoin-cli -regtest testmempoolaccept "[\"$DUST\"]"
# 기대: allowed false, reject-reason은 더스트 관련

echo "# 3. 금액을 0.00001(1,000 sat)로 올려 같은 과정 → allowed true"
RAW2=$(bitcoin-cli -regtest createrawtransaction '[]' "[{\"$BOB\":0.00001}]")
FUNDED2=$(bitcoin-cli -regtest -rpcwallet=alice fundrawtransaction $RAW2 | jq -r .hex)
SIGNED2=$(bitcoin-cli -regtest -rpcwallet=alice signrawtransactionwithwallet $FUNDED2 | jq -r .hex)
bitcoin-cli -regtest testmempoolaccept "[\"$SIGNED2\"]" | jq -c '.[] | {allowed, vsize}'

echo "# 2단계의 더스트 트랜잭션을 직접 채굴 (채굴자 직접 제출 재현)"
bitcoin-cli -regtest generateblock \
  $(bitcoin-cli -regtest -rpcwallet=miner getnewaddress) "[\"$DUST\"]"
DUST_TXID=$(bitcoin-cli -regtest decoderawtransaction "$DUST" | jq -r .txid)
echo "더스트 트랜잭션 $DUST_TXID 확인 수: $(bitcoin-cli -regtest getrawtransaction "$DUST_TXID" true | jq .confirmations)"
echo "→ 정책으로 거부된 트랜잭션이 블록에는 정상적으로 들어간다 (합의상 유효)"
