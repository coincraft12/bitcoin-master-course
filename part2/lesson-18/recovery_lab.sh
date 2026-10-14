#!/usr/bin/env bash
# 4-5 실습 ①~⑤: 니모닉에서 Core 지갑 복구, 실패 실험, 파일 백업 (s45-lab1, s45-lab2).
# 저장소 최상위에서 실행: bash part2/lesson-18/recovery_lab.sh
# regtest 전용 테스트 니모닉만 쓴다. tprv와 listdescriptors true 출력은 니모닉과 같은 수준의 비밀이다.
set -euo pipefail
CLI="bitcoin-cli -regtest"
REC=part2/lesson-18/recover.py

checksum() { $CLI getdescriptorinfo "$1" | jq -r .checksum; }
unique_name() {   # 슬라이드 이름(recovered 등)을 쓰되, 리허설을 반복해 이미 있으면 뒤에 시각을 붙인다
  if $CLI listwalletdir | jq -e --arg n "$1" '.wallets[] | select(.name == $n)' > /dev/null; then
    echo "$1-$(date +%s)"
  else
    echo "$1"
  fi
}
new_blank_wallet() {
  $CLI -named createwallet wallet_name="$(unique_name "$1")" blank=true | jq -r .name
}

# 1. 테스트 니모닉 생성 → m/84h/1h/0h/0/0 주소 계산 → 0.5 BTC 받기
OUT=$(python3 $REC new); echo "$OUT"
MNEMONIC=$(echo "$OUT" | sed -n 's/^니모닉   : //p')
FIRST=$(echo "$OUT" | sed -n 's/^첫 주소  : //p')
eval "$(echo "$OUT" | grep -E '^(RECV|CHG)=')"
$CLI -rpcwallet=alice sendtoaddress "$FIRST" 0.5
$CLI -rpcwallet=miner -generate 1 > /dev/null      # 슬라이드는 -rpcwallet 없이 -generate (ERRATA 참고)

# 2. 디스크립터 2줄에 체크섬 붙이기
RECV_D="$RECV#$(checksum "$RECV")"
CHG_D="$CHG#$(checksum "$CHG")"

# 3. 빈 지갑에 가져오기 → 잔액 0.5 확인
W=$(new_blank_wallet recovered)
$CLI -rpcwallet="$W" importdescriptors "[
  {\"desc\":\"$RECV_D\",\"active\":true,\"internal\":false,\"timestamp\":0},
  {\"desc\":\"$CHG_D\",\"active\":true,\"internal\":true,\"timestamp\":0}]" | jq -c '.[].success'
echo "[$W] 복구 지갑 잔액:"; $CLI -rpcwallet="$W" getbalances | jq .mine
echo "[$W] 첫 주소 $FIRST 가 내 주소인가:"
$CLI -rpcwallet="$W" getaddressinfo "$FIRST" | jq -c '{ismine, hdkeypath}'

# 4. 실패 실험: pkh + 44h 경로, 패스프레이즈 → 잔액 0 (4-3 체크리스트 재현)
for ARGS in "--purpose 44" "--passphrase TREZOR"; do
  # shellcheck disable=SC2086
  eval "$(python3 $REC show "$MNEMONIC" $ARGS | grep -E '^(RECV|CHG)=')"
  F=$(new_blank_wallet fail)
  $CLI -rpcwallet="$F" importdescriptors "[
    {\"desc\":\"$RECV#$(checksum "$RECV")\",\"active\":true,\"internal\":false,\"timestamp\":0},
    {\"desc\":\"$CHG#$(checksum "$CHG")\",\"active\":true,\"internal\":true,\"timestamp\":0}]" > /dev/null
  echo "[$F] ($ARGS) 잔액: $($CLI -rpcwallet="$F" getbalances | jq .mine.trusted)"
done

# 5. 파일 백업과 복원
BAK=/tmp/rec-$(date +%s).bak
$CLI -rpcwallet="$W" backupwallet "$BAK"
COPY=$(unique_name "${W}_copy")
$CLI restorewallet "$COPY" "$BAK" | jq -c .
echo "[$COPY] 잔액:"; $CLI -rpcwallet="$COPY" getbalances | jq .mine
