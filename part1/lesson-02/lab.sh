#!/usr/bin/env bash
# 1-2 LAB: 내 노드에서 제네시스 블록 보기
# 준비: regtest 노드 실행 중 (bitcoind -regtest -daemon, 2강), jq 설치
# 실행: 저장소 최상위에서 part1/lesson-02/lab.sh
set -e

# 1. 블록 0의 코인베이스 입력을 꺼낸다
# regtest도 메인넷과 같은 제네시스 코인베이스를 갖는다
H0=$(bitcoin-cli -regtest getblockhash 0)
bitcoin-cli -regtest getblock $H0 2 | jq -r '.tx[0].vin[0].coinbase' > genesis_cb.hex

# 2. 바이트를 문자로 출력해 헤드라인 문구를 찾는다
python3 -c "print(bytes.fromhex(open('genesis_cb.hex').read().strip()))"

# 3. 메인넷 제네시스 해시와 비교한다
MAINNET_H0=000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
echo "regtest 블록 0 해시: $H0"
echo "mainnet 블록 0 해시: $MAINNET_H0"
echo "---- regtest 블록 0 헤더 (time, nonce, bits, merkleroot) ----"
bitcoin-cli -regtest getblock $H0 1 | jq '{time, nonce, bits, merkleroot}'
