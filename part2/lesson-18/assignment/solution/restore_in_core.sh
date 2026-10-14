#!/usr/bin/env bash
# 2부 미니 과제 02 정답 예시: 테스트 니모닉을 Core에 디스크립터로 복원하고 주소를 대조한다.
# 저장소 최상위에서 실행: bash part2/lesson-18/assignment/solution/restore_in_core.sh ["<테스트 니모닉>"]
# 캡처할 화면: 아래 '대조' 블록 (계산값과 Core 값이 나란히 나온다). tprv가 화면에 남지 않게 주의.
set -euo pipefail
CLI="bitcoin-cli -regtest"
SOL=part2/lesson-18/assignment/solution/solution_recovery_kit.py
MNEMONIC=${1:-"abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"}

OUT=$(python3 $SOL "$MNEMONIC")
eval "$(echo "$OUT" | grep -E '^(RECV|CHG)(84|86)=')"
mapfile -t MINE < <(echo "$OUT" | grep -E '^  bcrt1' | sed 's/^  //')

cs() { $CLI getdescriptorinfo "$1" | jq -r .checksum; }
NAME="kit-$(date +%s)"
$CLI -named createwallet wallet_name="$NAME" blank=true > /dev/null
$CLI -rpcwallet="$NAME" importdescriptors "[
  {\"desc\":\"$RECV84#$(cs "$RECV84")\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$CHG84#$(cs "$CHG84")\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"},
  {\"desc\":\"$RECV86#$(cs "$RECV86")\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$CHG86#$(cs "$CHG86")\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]" | jq -c '[.[].success]'

echo "== 대조 (지갑 $NAME) =="
for i in 0 1 2; do
  echo "BIP84 #$i 계산 ${MINE[$i]}  Core $($CLI -rpcwallet="$NAME" getnewaddress "" bech32)"
done
for i in 0 1 2; do
  echo "BIP86 #$i 계산 ${MINE[$((i + 3))]}  Core $($CLI -rpcwallet="$NAME" getnewaddress "" bech32m)"
done
