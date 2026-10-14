#!/usr/bin/env bash
# 13-2 실습 ①~④: 노드 정보, 자금, 채널 열기, 결제, 종료 (s132-lab1, s132-lab2)
# 환경: Polar — bitcoind(regtest) 1개 + LND 노드 alice, bob. 슬라이드는 LND 0.21.4 + Core 31.1.
#
# 슬라이드 방식은 Polar 화면에서 노드별 "Terminal"을 열어 lncli 명령을 직접 치는 것이다.
# 이 스크립트는 같은 명령을 docker exec로 묶었다. 컨테이너 이름·접속 정보는 Polar 버전과
# 네트워크 번호에 따라 다를 수 있으니 아래 변수로 바꾼다 (docker ps로 확인).
# ※ 이 저장소 작성 환경에는 Polar·LND가 없어 실행 검증을 하지 못했다 (bash -n, shellcheck만 통과).
#
#   bash part5/lesson-54/lnd_lab.sh            # ①~④
#   FORCE=1 bash part5/lesson-54/lnd_lab.sh    # ④ 뒤에 새 채널을 열어 강제 종료까지
set -e
N="${POLAR_NET:-1}"
ALICE="${ALICE:-docker exec polar-n$N-alice lncli --network=regtest}"
BOB="${BOB:-docker exec polar-n$N-bob lncli --network=regtest}"
BTC="${BTC:-docker exec polar-n$N-backend1 bitcoin-cli -regtest -rpcuser=polaruser -rpcpassword=polarpass}"
BOB_HOST="${BOB_HOST:-polar-n$N-bob}"
HERE="$(cd "$(dirname "$0")" && pwd)"

mine() {   # 블록 n개를 만들고 두 LND가 따라잡을 때까지 기다린다
  $BTC generatetoaddress "$1" "$($BTC getnewaddress)" >/dev/null
  for _ in $(seq 1 30); do
    [ "$($ALICE getinfo | jq -r .synced_to_chain)" = "true" ] && \
    [ "$($BOB getinfo | jq -r .synced_to_chain)" = "true" ] && return 0
    sleep 1
  done
  echo "LND가 블록을 따라잡지 못했습니다"; return 1
}
# bitcoind 지갑 준비 (Polar가 이미 만들어 두었으면 그대로)
$BTC getwalletinfo >/dev/null 2>&1 || $BTC createwallet lab >/dev/null 2>&1 || $BTC loadwallet lab >/dev/null
if [ "$(jq -n "$($BTC getbalance) < 2")" = "true" ]; then mine 101; fi

echo "== ① 노드 정보와 자금 (alice 터미널) =="
$ALICE getinfo | jq '{identity_pubkey, block_height, num_active_channels}'
ADDR=$($ALICE newaddress p2tr | jq -r .address)
echo "alice Taproot 주소: $ADDR"
$BTC sendtoaddress "$ADDR" 1 >/dev/null          # bitcoind로 alice 주소에 1 BTC 입금
mine 6                                            # 후 블록 6개
$ALICE walletbalance | jq '{confirmed_balance}'

echo "== ② 채널 열기 =="
BOB_PUB=$($BOB getinfo | jq -r .identity_pubkey)
$ALICE connect "$BOB_PUB@$BOB_HOST:9735" >/dev/null 2>&1 || echo "(이미 연결됨)"
$ALICE openchannel --node_key "$BOB_PUB" --local_amt 1000000
mine 6                                            # 블록 6개 생성 후
$ALICE listchannels | jq '.channels[] | {channel_point, capacity, local_balance, remote_balance, commitment_type}'
CP=$($ALICE listchannels | jq -r '.channels[-1].channel_point')
FUND_TXID=${CP%:*}; FUND_IDX=${CP#*:}
echo "펀딩 출력 $CP:"
$BTC gettxout "$FUND_TXID" "$FUND_IDX" | jq '{value, type: .scriptPubKey.type}'

echo "== ③ 결제 =="
PAYREQ=$($BOB addinvoice --amt 25000 --memo "coffee" | jq -r .payment_request)   # bob
echo "인보이스: ${PAYREQ:0:40}…"
$ALICE decodepayreq "$PAYREQ" | jq '{num_satoshis, payment_hash, expiry, destination}'
HASH=$($ALICE decodepayreq "$PAYREQ" | jq -r .payment_hash)
H0=$($BTC getblockcount); M0=$($BTC getmempoolinfo | jq .size)
$ALICE payinvoice --force "$PAYREQ" >/dev/null   # 슬라이드는 확인 질문에 yes. --force가 질문을 건너뛴다
$ALICE listchannels | jq '.channels[] | {local_balance, remote_balance}'
echo "블록 수 $H0 → $($BTC getblockcount), 멤풀 $M0 → $($BTC getmempoolinfo | jq .size)건 (그대로여야 한다)"
PRE=$($ALICE listpayments | jq -r --arg h "$HASH" '.payments[] | select(.payment_hash == $h) | .payment_preimage')
python3 "$HERE/check_preimage.py" "$PRE" "$HASH"

echo "== ④ 협력 종료 =="
CLOSE=$($ALICE closechannel --funding_txid "$FUND_TXID" --output_index "$FUND_IDX" | jq -r .closing_txid)
mine 6
echo "종료 txid $CLOSE 출력:"
for i in 0 1; do $BTC gettxout "$CLOSE" $i | jq -c '{value, address: .scriptPubKey.address}'; done
python3 "$HERE/channel_math.py"

if [ "${FORCE:-0}" = "1" ]; then
  echo "== 추가: 강제 종료 =="
  $ALICE openchannel --node_key "$BOB_PUB" --local_amt 1000000 >/dev/null
  mine 6
  CP=$($ALICE listchannels | jq -r '.channels[-1].channel_point')
  $ALICE closechannel --force --funding_txid "${CP%:*}" --output_index "${CP#*:}" >/dev/null
  mine 1
  $ALICE pendingchannels | jq '.pending_force_closing_channels[] | {limbo_balance, blocks_til_maturity}'
fi
