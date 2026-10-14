#!/usr/bin/env bash
# 최종 프로젝트 풀이: Taproot 볼트 지갑 구성과 운영 (s14-final 01~03)
#   tr(키 경로, {multi_a(2,K1,K2,K3), and_v(v:pk(R),older(N))})
#   키 경로: 단일 키(fp_owner) — MUSIG=1이면 musig(K1,K2) (2-of-2 MuSig2, Core 31부터 지갑 서명)
# 기본은 regtest에서 끝까지 자동으로 돈다. 과제 제출은 NETWORK=signet으로 같은 흐름을 밟는다
# (signet 노드 동기화 필요, 입금은 signet 파우셋에서 직접 — 스크립트가 확인될 때까지 기다린다).
# ※ 작성 환경에는 노드가 없어 bash -n·shellcheck와 디스크립터·주소 계산(vault_descriptor.py)만 확인했다.
#   MUSIG=1의 2라운드 서명 흐름은 특히 실행 검증하지 못했다.
#
#   bash part5/lesson-60/final_project/solution/vault_wallet.sh
#   OLDER=144 NETWORK=signet bash part5/lesson-60/final_project/solution/vault_wallet.sh
#   MUSIG=1 bash part5/lesson-60/final_project/solution/vault_wallet.sh
set -e
NETWORK="${NETWORK:-regtest}"
OLDER="${OLDER:-20}"               # 실습용. 실제 설계는 52,560(약 1년) 등 → 설계서에 이유를 쓴다
MUSIG="${MUSIG:-0}"
CLI="bitcoin-cli -$NETWORK"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="python3 $HERE/vault_descriptor.py"
VAULT="vault_${NETWORK}_${OLDER}_m${MUSIG}"
OUT="${OUT:-/tmp/$VAULT.txt}"      # 제출물 메모 (공개 디스크립터, txid)

loaded() { $CLI -rpcwallet="$1" getwalletinfo >/dev/null 2>&1 || $CLI loadwallet "$1" >/dev/null 2>&1; }
tr_xpub() {    # 받는용 tr() 디스크립터의 [지문/86h/…]tpub
  $CLI -rpcwallet="$1" listdescriptors \
    | jq -r '.descriptors[] | select((.desc | startswith("tr(")) and .internal == false) | .desc' \
    | grep -o '\[.*\][a-zA-Z0-9]*'
}
confirm() {    # 블록 하나 (regtest) 또는 확인될 때까지 대기 (signet)
  if [ "$NETWORK" = regtest ]; then $CLI -rpcwallet=miner -generate 1 >/dev/null
  else
    until [ "$($CLI -rpcwallet="$VAULT" gettransaction "$1" | jq .confirmations)" -ge 1 ]; do sleep 30; done
  fi
}

echo "== 01 키 5개 (서로 다른 지갑 = 서로 다른 장비라고 가정) =="
for W in fp_owner fp_k1 fp_k2 fp_k3 fp_rescue; do
  loaded $W || $CLI createwallet $W >/dev/null
done
K0=$(tr_xpub fp_owner); K1=$(tr_xpub fp_k1); K2=$(tr_xpub fp_k2); K3=$(tr_xpub fp_k3); R=$(tr_xpub fp_rescue)
ARGS=(--k1 "$K1" --k2 "$K2" --k3 "$K3" --rescue "$R" --older "$OLDER")
if [ "$MUSIG" = 1 ]; then ARGS+=(--musig); else ARGS+=(--keypath "$K0"); fi
mapfile -t D < <($PY build "${ARGS[@]}" --quiet)
EXT=${D[0]}; INT=${D[1]}
# 파이썬이 붙인 체크섬과 Core의 체크섬이 같은지
for X in "$EXT" "$INT"; do
  [ "$($CLI getdescriptorinfo "$X" | jq -r .checksum)" = "${X##*#}" ] || { echo "체크섬 불일치: $X"; exit 1; }
done
echo "EXT=$EXT"

echo "== 02 워치온리 지갑에 가져와 주소 생성 =="
FRESH=0
if ! loaded "$VAULT"; then
  $CLI -named createwallet wallet_name="$VAULT" disable_private_keys=true blank=true >/dev/null
  $CLI -rpcwallet="$VAULT" importdescriptors "[
    {\"desc\":\"$EXT\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
    {\"desc\":\"$INT\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c 'map(.success)'
  FRESH=1
fi
ADDR=$($CLI -rpcwallet="$VAULT" getnewaddress "" bech32m)
echo "Core 주소      : $ADDR"
if [ "$FRESH" = 1 ] && [ "$MUSIG" = 0 ]; then
  echo "파이썬 계산 /0/0: $($PY address "$EXT" --network "$NETWORK" --count 1)   (같아야 한다)"
fi

echo "== 03 입금 =="
if [ "$NETWORK" = regtest ]; then
  loaded miner || { echo "miner 지갑이 없습니다. bash env/setup_regtest.sh"; exit 1; }
  FUND=$($CLI -rpcwallet=miner sendtoaddress "$ADDR" 1)
else
  echo "signet 파우셋에서 $ADDR 로 입금하세요. 확인될 때까지 기다립니다…"
  until [ "$($CLI -rpcwallet="$VAULT" listunspent 1 | jq length)" -ge 1 ]; do sleep 30; done
  FUND=$($CLI -rpcwallet="$VAULT" listunspent 1 | jq -r '.[0].txid')
fi
confirm "$FUND"
echo "입금 txid $FUND"
DEST=$($CLI -rpcwallet="$VAULT" getrawchangeaddress bech32m)     # 실습 송금은 볼트 자기 잔돈 주소로 (자금 보존)

new_psbt() {   # $1 = 입력 sequence (없으면 지갑 기본)
  if [ -n "$1" ]; then
    local u; u=$($CLI -rpcwallet="$VAULT" listunspent 1 | jq -c '.[0] | {txid, vout}')
    $CLI -rpcwallet="$VAULT" walletcreatefundedpsbt \
      "[{\"txid\":$(echo "$u" | jq .txid),\"vout\":$(echo "$u" | jq .vout),\"sequence\":$1}]" \
      "[{\"$DEST\":0.1}]" 0 '{"add_inputs":false,"fee_rate":5}' | jq -r .psbt
  else
    $CLI -rpcwallet="$VAULT" walletcreatefundedpsbt '[]' "[{\"$DEST\":0.1}]" 0 '{"fee_rate":5}' | jq -r .psbt
  fi
}
sign_all() {   # PSBT를 지갑들이 각자 서명 → combinepsbt
  local psbt=$1; shift
  local parts=() w
  for w in "$@"; do parts+=("\"$($CLI -rpcwallet="$w" walletprocesspsbt "$psbt" | jq -r .psbt)\""); done
  $CLI combinepsbt "[$(IFS=,; echo "${parts[*]}")]"
}
broadcast() {  # $1 = 이름, $2 = 완성 전 PSBT
  local hex txid
  hex=$($CLI finalizepsbt "$2" | jq -r .hex)
  [ "$hex" != null ] || { echo "$1: 서명이 모자라 완성되지 않았다"; $CLI analyzepsbt "$2" | jq -c .; exit 1; }
  txid=$($CLI sendrawtransaction "$hex")
  confirm "$txid"
  local wit kind
  wit=$($CLI decoderawtransaction "$hex" | jq -c '.vin[0].txinwitness | map(length/2)')
  # witness 항목이 1개면 키 경로, 아니면 스크립트 경로 (마지막 두 항목 = 리프 스크립트, 컨트롤 블록)
  if [ "$(echo "$wit" | jq length)" = 1 ]; then kind="실제: 키 경로"; else kind="실제: 스크립트 경로"; fi
  echo "$1 txid $txid  witness 바이트 $wit ($kind)"
  echo "$1 txid $txid ($kind)" >> "$OUT"
}

{ echo "공개 디스크립터 (받는용)"; echo "$EXT"; echo "공개 디스크립터 (잔돈용)"; echo "$INT"; echo "입금 txid $FUND"; } > "$OUT"

echo "== PSBT로 서명을 모아 송금 =="
if [ "$MUSIG" = 1 ]; then
  # MuSig2: 1라운드(논스) → 합치기 → 2라운드(부분 서명) → 합치기. Core 31 지갑 흐름 (실행 검증 불가)
  P=$(new_psbt "")
  R1=$(sign_all "$P" fp_k1 fp_k2)
  R2=$(sign_all "$R1" fp_k1 fp_k2)
  broadcast "키 경로 (MuSig2 K1+K2)" "$R2"
else
  broadcast "키 경로 (소유자 단독)" "$(sign_all "$(new_psbt "")" fp_owner)"
fi
broadcast "스크립트 경로 2-of-3 (K1+K3)" "$(sign_all "$(new_psbt "")" fp_k1 fp_k3)"

if [ "$NETWORK" = regtest ]; then
  echo "== 복구 경로 리허설: $OLDER블록 미사용 후 R 단독 =="
  $CLI -rpcwallet=miner -generate "$OLDER" >/dev/null
  broadcast "복구 경로 (R, sequence $OLDER)" "$(sign_all "$(new_psbt "$OLDER")" fp_rescue)"
else
  echo "(signet: 복구 경로는 $OLDER블록 뒤 같은 명령으로. 설계서에 절차를 적는다)"
fi
echo "제출물 메모: $OUT (공개 정보만. 개인키·니모닉은 넣지 않는다)"
