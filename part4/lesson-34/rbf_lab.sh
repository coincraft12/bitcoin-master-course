#!/usr/bin/env bash
# 8-3 실습 ①~④: 낮은 수수료로 보내고 올리기, 내 주소로 되돌려 사실상 취소 (s83-lab1, s83-lab2).
# 저장소 최상위에서 실행: bash part4/lesson-34/rbf_lab.sh
# 필요: regtest 노드, miner·alice·bob 지갑(env/setup_regtest.sh), jq. bumpfee outputs 옵션은 Core 25~.
set -uo pipefail

echo "# 시작 전 bob 잔액"
bitcoin-cli -regtest -rpcwallet=bob getbalances | jq -c .mine

# 1. 1 sat/vB로 송금
BOB=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
TX1=$(bitcoin-cli -regtest -rpcwallet=alice -named sendtoaddress address=$BOB amount=0.1 fee_rate=1)
echo "TX1=$TX1"
bitcoin-cli -regtest getmempoolentry $TX1 | jq '{vsize, fees}'
echo "# bob 지갑에는 '대기 중'으로 보인다"
bitcoin-cli -regtest -rpcwallet=bob getbalances | jq -c .mine
# 2. 10 sat/vB로 올리기
TX2=$(bitcoin-cli -regtest -rpcwallet=alice -named bumpfee $TX1 options='{"fee_rate":10}' | jq -r .txid)
echo "TX2=$TX2"
bitcoin-cli -regtest getmempoolentry $TX1        # 오류: 멤풀에 없음
bitcoin-cli -regtest getmempoolentry $TX2 | jq '{vsize, fees}'

echo "# TX1과 TX2 비교: 입력은 같고, txid가 바뀌고, 잔돈 출력이 줄었다"
for T in $TX1 $TX2; do
  bitcoin-cli -regtest -rpcwallet=alice gettransaction $T true \
    | jq -c '{txid, vin: [.decoded.vin[] | "\(.txid):\(.vout)"], vout: [.decoded.vout[] | {value, address: .scriptPubKey.address}]}'
done

# 3. 출력을 내 주소로 바꿔 대체 (bumpfee outputs 옵션: Core 25~)
ME=$(bitcoin-cli -regtest -rpcwallet=alice getnewaddress)
bitcoin-cli -regtest -rpcwallet=alice -named bumpfee $TX2 \
  options="{\"fee_rate\":20,\"outputs\":[{\"$ME\":0.1}]}"
# 4. 확정 후 bob 잔액 확인
bitcoin-cli -regtest -rpcwallet=miner -generate 1
bitcoin-cli -regtest -rpcwallet=bob getbalances
echo "→ bob은 한때 '대기 중 0.1 BTC'를 보았지만 결국 받지 못했다 (0-확인 결제 위험의 재현)"
