#!/usr/bin/env bash
# 12-4 실습 ①~④: 상속 지갑 (s124-lab1, s124-lab2, s124-lab3)
#   정책: or(pk(본인), and(pk(가족), older(N))), 실습에서는 N = 20블록
#   participant_1 = 본인, participant_2 = 가족 (6-2에서 만든 지갑과 xpub 파일)
# 준비: env/setup_regtest.sh (miner, bob 지갑). 6-2의 xpub_1.txt, xpub_2.txt가 있는 폴더에서 실행하거나
#       XPUB_DIR=그 폴더 로 알려 준다. 없으면 (저장소 보완) 6-2 1단계를 그대로 돌려 새로 만든다.
#
#   bash part5/lesson-52/estate_lab.sh
set -e
CLI="bitcoin-cli -regtest"
XPUB_DIR="${XPUB_DIR:-.}"

loaded() { $CLI -rpcwallet="$1" getwalletinfo >/dev/null 2>&1 || $CLI loadwallet "$1" >/dev/null 2>&1; }
for W in miner bob; do
  loaded $W || { echo "$W 지갑이 없습니다. 먼저 bash env/setup_regtest.sh"; exit 1; }
done

# (저장소 보완) 6-2 s62-lab1 1단계: 참여자 지갑과 키 출처 포함 tpub 파일
if [ ! -f "$XPUB_DIR/xpub_1.txt" ] || [ ! -f "$XPUB_DIR/xpub_2.txt" ]; then
  echo "xpub 파일이 없어 6-2 1단계를 실행합니다 ($XPUB_DIR)"
  for n in 1 2 3; do loaded participant_$n || $CLI createwallet participant_$n >/dev/null; done
  for n in 1 2 3; do
    $CLI -rpcwallet=participant_$n listdescriptors \
      | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == false) | .desc' \
      | grep -o '\[.*\][a-zA-Z0-9]*' > "$XPUB_DIR/xpub_$n.txt"
  done
fi
for n in 1 2; do loaded participant_$n || { echo "participant_$n 지갑이 없습니다 (6-2)"; exit 1; }; done

echo "== ① 상속 지갑 만들기 (N = 20블록) =="
X1=$(cat "$XPUB_DIR/xpub_1.txt"); X2=$(cat "$XPUB_DIR/xpub_2.txt")      # 6-2: participant_1 = 본인, _2 = 가족
EXT="wsh(or_d(pk($X1/0/*),and_v(v:pk($X2/0/*),older(20))))"
INT="wsh(or_d(pk($X1/1/*),and_v(v:pk($X2/1/*),older(20))))"
EXT="$EXT#$($CLI getdescriptorinfo "$EXT" | jq -r .checksum)"
INT="$INT#$($CLI getdescriptorinfo "$INT" | jq -r .checksum)"
echo "EXT=$EXT"
if ! loaded estate; then
  $CLI -named createwallet wallet_name=estate \
    disable_private_keys=true blank=true >/dev/null
  $CLI -rpcwallet=estate importdescriptors "[
    {\"desc\":\"$EXT\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
    {\"desc\":\"$INT\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]"
fi
FUND=$($CLI -rpcwallet=miner sendtoaddress \
  "$($CLI -rpcwallet=estate getnewaddress)" 1)
$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "입금 txid $FUND (1확인)"

echo "== ② 가족이 너무 일찍 시도하면 =="
# (저장소 보완) 다시 실행해도 방금 입금한 UTXO를 고르도록 txid로 거른다. 슬라이드는 '.[0] | {txid, vout}'
U=$($CLI -rpcwallet=estate listunspent | jq -c --arg t "$FUND" '[.[] | select(.txid == $t)][0] | {txid, vout}')
TXID=$(echo "$U" | jq -r .txid); VOUT=$(echo "$U" | jq .vout)
DEST=$($CLI -rpcwallet=bob getnewaddress)
PSBT=$($CLI -rpcwallet=estate walletcreatefundedpsbt \
  "[{\"txid\":\"$TXID\",\"vout\":$VOUT,\"sequence\":20}]" \
  "[{\"$DEST\":0.5}]" 0 '{"add_inputs":false,"fee_rate":5}' | jq -r .psbt)
SIGNED=$($CLI -rpcwallet=participant_2 walletprocesspsbt "$PSBT" | jq -r .psbt)
HEX=$($CLI finalizepsbt "$SIGNED" | jq -r .hex)
if $CLI sendrawtransaction "$HEX"; then
  echo "!! 거부되어야 하는데 받아들여졌다"; exit 1
fi
echo "→ 거부(non-BIP68-final)가 정상이다. HEX는 ③에서 다시 쓴다."

echo "== ③ 20블록 후 같은 HEX가 성공 =="
$CLI -rpcwallet=miner -generate 20 >/dev/null
FAMILY_TXID=$($CLI sendrawtransaction "$HEX")      # 성공 → txid
FAMILY_HEX=$HEX
$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "가족 경로 txid $FAMILY_TXID"

echo "== ④ 새 입금 → sequence 지정 없이 participant_1(본인)이 서명 → 즉시 전파 =="
$CLI -rpcwallet=miner sendtoaddress "$($CLI -rpcwallet=estate getnewaddress)" 1 >/dev/null
$CLI -rpcwallet=miner -generate 1 >/dev/null
PSBT=$($CLI -rpcwallet=estate walletcreatefundedpsbt \
  '[]' "[{\"$DEST\":0.5}]" 0 '{"fee_rate":5}' | jq -r .psbt)
SIGNED=$($CLI -rpcwallet=participant_1 walletprocesspsbt "$PSBT" | jq -r .psbt)
OWNER_HEX=$($CLI finalizepsbt "$SIGNED" | jq -r .hex)
OWNER_TXID=$($CLI sendrawtransaction "$OWNER_HEX")
$CLI -rpcwallet=miner -generate 1 >/dev/null
echo "본인 경로 txid $OWNER_TXID"

echo "== witness 비교 (decoderawtransaction) =="
echo "본인 경로: [본인 서명] [witnessScript]"
$CLI decoderawtransaction "$OWNER_HEX" | jq -c '.vin[0].txinwitness | map(length/2)'
echo "가족 경로: [가족 서명] [빈 값] [witnessScript]"
$CLI decoderawtransaction "$FAMILY_HEX" | jq -c '.vin[0].txinwitness | map(length/2)'
echo "witnessScript:"
$CLI decodescript "$($CLI decoderawtransaction "$FAMILY_HEX" | jq -r '.vin[0].txinwitness[-1]')" | jq -r .asm
