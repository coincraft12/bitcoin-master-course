#!/usr/bin/env bash
# 12-2 실습: 파일로 왕복하는 오프라인 서명 (s122-lab)
# 5-4의 watch(온라인, 키 없음)와 signer(오프라인, 키 보유) 구성을 그대로 쓰고,
# PSBT를 파일로 주고받아 기기 간 전달을 재현한다.
# 준비: env/setup_regtest.sh (miner, alice, bob 지갑). watch·signer가 없으면 0단계가 5-4 방식으로 만든다.
#
#   bash part5/lesson-50/offline_signing.sh
set -e
CLI="bitcoin-cli -regtest"
HERE="$(cd "$(dirname "$0")" && pwd)"

loaded() { $CLI -rpcwallet="$1" getwalletinfo >/dev/null 2>&1 || $CLI loadwallet "$1" >/dev/null 2>&1; }

# 0) (저장소 보완) 5-4 구성 확인. 이미 있으면 그대로 쓴다.
for W in miner bob; do
  loaded $W || { echo "$W 지갑이 없습니다. 먼저 bash env/setup_regtest.sh"; exit 1; }
done
loaded signer || $CLI createwallet signer >/dev/null
if ! loaded watch; then
  $CLI -named createwallet wallet_name=watch disable_private_keys=true blank=true >/dev/null
  RECV=$($CLI -rpcwallet=signer listdescriptors \
    | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == false) | .desc')
  CHG=$($CLI -rpcwallet=signer listdescriptors \
    | jq -r '.descriptors[] | select((.desc | startswith("wpkh(")) and .internal == true) | .desc')
  $CLI -rpcwallet=watch importdescriptors "[{\"desc\":\"$RECV\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$CHG\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" >/dev/null
fi
if [ "$(jq -n "$($CLI -rpcwallet=watch getbalance) < 0.2")" = "true" ]; then
  $CLI -rpcwallet=miner sendtoaddress "$($CLI -rpcwallet=watch getnewaddress "" bech32)" 1 >/dev/null
  $CLI -rpcwallet=miner -generate 1 >/dev/null
fi
echo "watch 잔액: $($CLI -rpcwallet=watch getbalance) BTC (키 없음)"

echo "== 온라인 측: PSBT 작성 후 파일로 =="
BOB=$($CLI -rpcwallet=bob getnewaddress)
$CLI -rpcwallet=watch walletcreatefundedpsbt '[]' \
  "[{\"$BOB\":0.1}]" 0 '{"fee_rate":5}' | jq -r .psbt > /tmp/unsigned.psbt
echo "$BOB" > /tmp/intended_address.txt     # 받는 사람이 다른 경로(전화·대면)로 알려 준 주소라고 가정
echo "unsigned.psbt $(wc -c < /tmp/unsigned.psbt)바이트, 받는 주소 $BOB"

echo "== 오프라인 측: 서명 전 내용 확인 → 서명 =="
$CLI decodepsbt "$(cat /tmp/unsigned.psbt)" \
  | jq '{outputs: [.tx.vout[] | {value, address: .scriptPubKey.address}], fee}'
# (저장소 보완) 체크리스트 5개를 스크립트로 확인. 실패하면 서명하지 않고 멈춘다.
python3 "$HERE/check_psbt.py" /tmp/unsigned.psbt "$(cat /tmp/intended_address.txt)" 0.1
$CLI -rpcwallet=signer walletprocesspsbt "$(cat /tmp/unsigned.psbt)" \
  | jq -r .psbt > /tmp/signed.psbt

echo "== 온라인 측: 완성 후 전파 =="
HEX=$($CLI finalizepsbt "$(cat /tmp/signed.psbt)" | jq -r .hex)
$CLI sendrawtransaction "$HEX"
$CLI -rpcwallet=miner -generate 1 >/dev/null

echo "== 심화: 받는 주소를 바꾼 PSBT를 확인 단계에서 잡아내기 =="
$CLI -rpcwallet=watch walletcreatefundedpsbt '[]' \
  "[{\"$BOB\":0.1}]" 0 '{"fee_rate":5}' | jq -r .psbt > /tmp/unsigned.psbt
EVIL=$($CLI -rpcwallet=miner getnewaddress)       # 공격자 주소 역할
python3 "$HERE/tamper_psbt.py" /tmp/unsigned.psbt "$EVIL" /tmp/tampered.psbt
if python3 "$HERE/check_psbt.py" /tmp/tampered.psbt "$(cat /tmp/intended_address.txt)" 0.1; then
  echo "!! 변조를 잡지 못했다"; exit 1
else
  echo "→ 변조된 PSBT는 서명하지 않았다."
fi
