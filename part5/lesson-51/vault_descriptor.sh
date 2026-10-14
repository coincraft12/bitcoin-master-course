#!/usr/bin/env bash
# 12-3 볼트 설계서 06 "디스크립터 초안"을 regtest에서 확인하고 출금 정책을 리허설한다 (s123-vault, s123-lab).
#   키 A = participant_1 (대표이사), B = participant_2 (재무책임자), C = participant_3 (외부 수탁·대여금고)
#   확장: 장기 미사용 시 별도 복구 키 R(vault_recovery 지갑)이 열리는 타임락 리프 (6-5, 12-4)
#   초안 ① 6-2 문법: wsh(sortedmulti(2,A,B,C))
#   초안 ② 6-5 문법: tr(NUMS,{multi_a(2,A,B,C),and_v(v:pk(R),older(OLDER))})  ← 키 경로 없음
# 리허설: 평시 A+B 출금, A 부재 시 B+C 출금. OLDER를 작게 주면(예: OLDER=20) R 단독 복구도 리허설한다.
# 준비: env/setup_regtest.sh. 6-2의 xpub_1~3.txt가 있는 폴더에서 실행하거나 XPUB_DIR로 알려 준다.
#
#   bash part5/lesson-51/vault_descriptor.sh              # OLDER=52560 (약 1년), 복구 리허설 생략
#   OLDER=20 bash part5/lesson-51/vault_descriptor.sh     # 복구 리프까지 리허설
set -e
CLI="bitcoin-cli -regtest"
XPUB_DIR="${XPUB_DIR:-.}"
OLDER="${OLDER:-52560}"          # 1년 ≈ 52,560블록, 상대 타임락 상한 65,535
NUMS=50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0   # 6-5 NUMS 점

loaded() { $CLI -rpcwallet="$1" getwalletinfo >/dev/null 2>&1 || $CLI loadwallet "$1" >/dev/null 2>&1; }
for W in miner bob; do
  loaded $W || { echo "$W 지갑이 없습니다. 먼저 bash env/setup_regtest.sh"; exit 1; }
done
xpub_of() {   # 6-2 s62-lab1과 같은 추출: 받는용 wpkh 디스크립터의 [지문/경로]tpub
  $CLI -rpcwallet="$1" listdescriptors \
    | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == false) | .desc' \
    | grep -o '\[.*\][a-zA-Z0-9]*'
}
for n in 1 2 3; do
  loaded participant_$n || $CLI createwallet participant_$n >/dev/null
  [ -f "$XPUB_DIR/xpub_$n.txt" ] || xpub_of participant_$n > "$XPUB_DIR/xpub_$n.txt"
done
loaded vault_recovery || $CLI createwallet vault_recovery >/dev/null
A=$(cat "$XPUB_DIR/xpub_1.txt"); B=$(cat "$XPUB_DIR/xpub_2.txt"); C=$(cat "$XPUB_DIR/xpub_3.txt")
R=$(xpub_of vault_recovery)

with_checksum() { echo "$1#$($CLI getdescriptorinfo "$1" | jq -r .checksum)"; }
make_watch() {   # $1 지갑 이름, $2 받는용, $3 잔돈용
  loaded "$1" && return 0
  $CLI -named createwallet wallet_name="$1" disable_private_keys=true blank=true >/dev/null
  $CLI -rpcwallet="$1" importdescriptors "[
    {\"desc\":\"$2\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
    {\"desc\":\"$3\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c 'map(.success)'
}

echo "== 초안 ① wsh(sortedmulti) — 6-2 문법 =="
W_EXT=$(with_checksum "wsh(sortedmulti(2,$A/0/*,$B/0/*,$C/0/*))")
W_INT=$(with_checksum "wsh(sortedmulti(2,$A/1/*,$B/1/*,$C/1/*))")
echo "$W_EXT"
make_watch vault_wsh "$W_EXT" "$W_INT"
echo "첫 주소: $($CLI -rpcwallet=vault_wsh getnewaddress)"

echo "== 초안 ② tr(NUMS, {2-of-3 CHECKSIGADD, 복구 키 + older($OLDER)}) — 6-5 문법 =="
T_EXT=$(with_checksum "tr($NUMS,{multi_a(2,$A/0/*,$B/0/*,$C/0/*),and_v(v:pk($R/0/*),older($OLDER))})")
T_INT=$(with_checksum "tr($NUMS,{multi_a(2,$A/1/*,$B/1/*,$C/1/*),and_v(v:pk($R/1/*),older($OLDER))})")
echo "$T_EXT"
make_watch "vault_tr_$OLDER" "$T_EXT" "$T_INT"
VAULT="vault_tr_$OLDER"
echo "첫 주소: $($CLI -rpcwallet="$VAULT" getnewaddress "" bech32m)"

spend() {   # $1 금액, $2 sequence(없으면 빈 값), 나머지 = 서명할 지갑들
  local amt=$1 seq=$2; shift 2
  local dest psbt parts=() p combined hex
  dest=$($CLI -rpcwallet=bob getnewaddress)
  if [ -n "$seq" ]; then
    local u; u=$($CLI -rpcwallet="$VAULT" listunspent | jq -c '.[0] | {txid, vout}')
    psbt=$($CLI -rpcwallet="$VAULT" walletcreatefundedpsbt \
      "[{\"txid\":$(echo "$u" | jq .txid),\"vout\":$(echo "$u" | jq .vout),\"sequence\":$seq}]" \
      "[{\"$dest\":$amt}]" 0 '{"add_inputs":false,"fee_rate":5}' | jq -r .psbt)
  else
    psbt=$($CLI -rpcwallet="$VAULT" walletcreatefundedpsbt '[]' "[{\"$dest\":$amt}]" 0 '{"fee_rate":5}' | jq -r .psbt)
  fi
  for w in "$@"; do
    p=$($CLI -rpcwallet="$w" walletprocesspsbt "$psbt" | jq -r .psbt)
    parts+=("\"$p\"")
  done
  combined=$($CLI combinepsbt "[$(IFS=,; echo "${parts[*]}")]")
  hex=$($CLI finalizepsbt "$combined" | jq -r .hex)
  $CLI sendrawtransaction "$hex"
  $CLI -rpcwallet=miner -generate 1 >/dev/null
  $CLI decoderawtransaction "$hex" | jq -c '.vin[0].txinwitness | map(length/2)'
}

$CLI -rpcwallet=miner sendtoaddress "$($CLI -rpcwallet="$VAULT" getnewaddress "" bech32m)" 2 >/dev/null
$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "== 평시 출금: A + B (participant_1, participant_2) =="
spend 0.3 "" participant_1 participant_2
echo "== A 부재 시: B + C (participant_2, participant_3) =="
spend 0.3 "" participant_2 participant_3
echo "witness 바이트 수: [서명 또는 빈 값 ×3(키 역순)] [리프 스크립트] [컨트롤 블록]"

if [ "$OLDER" -le 1000 ]; then
  echo "== 복구 리허설: $OLDER블록 미사용 후 R 단독 =="
  $CLI -rpcwallet=miner -generate "$OLDER" >/dev/null
  spend 0.3 "$OLDER" vault_recovery
else
  echo "(OLDER=$OLDER: 복구 리프 리허설은 OLDER=20 등 작은 값으로 다시 실행)"
fi
echo "vault 잔액: $($CLI -rpcwallet="$VAULT" getbalance) BTC"
