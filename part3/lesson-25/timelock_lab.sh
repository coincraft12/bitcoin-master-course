#!/usr/bin/env bash
# 6-3 LAB ①~④ (s63-lab1~3): 20블록 뒤에야 쓸 수 있는 코인 → 기한 전 지출 두 가지 → 기한 후 지출. 저장소 최상위에서 실행.
#   bash part3/lesson-25/timelock_lab.sh
# participant_1 지갑(6-2, lesson-24)이 있어야 한다. regtest 전용 키만! listdescriptors true는 개인키를 출력한다.
set -euo pipefail
CLI="bitcoin-cli -regtest"

# 1. 키와 만료 높이 (영상에서는 "regtest 전용" 자막을 반드시 표시)
TPRV=$($CLI -rpcwallet=participant_1 listdescriptors true \
  | jq -r '.descriptors[0].desc' | grep -o 'tprv[a-zA-Z0-9]*')
H=$(( $($CLI getblockcount) + 20 ))
DESC="wsh(and_v(v:pk($TPRV/7/*),after($H)))"
DESC="$DESC#$($CLI getdescriptorinfo "$DESC" | jq -r .checksum)"
echo "만료 높이 H=$H"
# 2. 지갑 tl에 가져오고 입금
$CLI -named createwallet wallet_name=tl blank=true > /dev/null 2>&1 || $CLI loadwallet tl > /dev/null 2>&1 || true
$CLI -rpcwallet=tl importdescriptors \
  "[{\"desc\":\"$DESC\",\"timestamp\":\"now\",\"range\":[0,5]}]" | jq -c '[.[].success]'
TL_ADDR=$($CLI deriveaddresses "$DESC" "[0,0]" | jq -r '.[0]')
# tl에는 활성(active) 디스크립터가 없어 지갑이 잔돈 주소를 만들지 못한다 → 같은 디스크립터 1번 주소를 잔돈으로 지정 (ERRATA s63-lab2)
TL_CHG=$($CLI deriveaddresses "$DESC" "[1,1]" | jq -r '.[0]')
OPT="{\"changeAddress\":\"$TL_CHG\"}"
echo "TL_ADDR=$TL_ADDR"
$CLI -rpcwallet=miner sendtoaddress "$TL_ADDR" 1 > /dev/null
$CLI -rpcwallet=miner -generate 1 > /dev/null

# 3. 기한 전 지출 시도 두 가지
BOB=$($CLI -rpcwallet=bob getnewaddress "" bech32)
NOW=$($CLI getblockcount)
echo "== (a) nLockTime=$NOW < 만료 높이: 스크립트 조건 미충족 =="
P=$($CLI -rpcwallet=tl walletcreatefundedpsbt '[]' "[{\"$BOB\":0.5}]" "$NOW" "$OPT" | jq -r .psbt)
$CLI -rpcwallet=tl walletprocesspsbt "$P" | jq .complete
echo "== (b) nLockTime=$H = 만료 높이: 서명은 되지만 아직 그 높이가 아님 =="
P=$($CLI -rpcwallet=tl walletcreatefundedpsbt '[]' "[{\"$BOB\":0.5}]" "$H" "$OPT" | jq -r .psbt)
S=$($CLI -rpcwallet=tl walletprocesspsbt "$P" | jq -r .psbt)
HEX=$($CLI finalizepsbt "$S" | jq -r .hex)
echo "$HEX" > tl_spend.hex                       # 4단계에서 같은 바이트를 다시 보낸다
$CLI sendrawtransaction "$HEX" || echo "→ 기대한 거부: non-final (트랜잭션 유효 시점 문제)"

# 4. 기한 후 지출: 3단계 (b)의 hex 그대로
$CLI -rpcwallet=miner -generate 20 > /dev/null
$CLI sendrawtransaction "$HEX"
echo "→ 같은 바이트가 이번엔 받아들여졌다. 새로 만든 트랜잭션이 아니다."
$CLI -rpcwallet=miner -generate 1 > /dev/null
