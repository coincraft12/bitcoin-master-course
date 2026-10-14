#!/usr/bin/env bash
# 4-4 실습 ①~④: 내 지갑 디스크립터로 주소 재현, 워치온리 지갑, 체크섬 실험 (s44-lab1, s44-lab2).
# 저장소 최상위에서 실행: bash part2/lesson-17/descriptor_lab.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"

echo "# 1. 디스크립터 8개 보기 → 함수·지문·경로(84h/1h/0h)를 해부도와 대조"
$CLI -rpcwallet=alice listdescriptors | jq '.descriptors[] | {desc, internal, active}'

echo "# 2. 지갑 없이 디스크립터만으로 주소 5개"
DESC=$($CLI -rpcwallet=alice listdescriptors \
  | jq -r '.descriptors[] | select((.desc|startswith("wpkh(")) and .internal==false) | .desc')
echo "DESC=$DESC"
$CLI getdescriptorinfo "$DESC"
$CLI deriveaddresses "$DESC" "[0,4]"
echo "# 같은 디스크립터를 lib로 펼친 결과"
python3 part2/lesson-17/descriptor_offline.py "$DESC" 0 4
echo "# alice의 getnewaddress (이미 쓴 지갑이면 시작 인덱스가 0이 아닐 수 있다)"
for _ in 1 2 3; do $CLI -rpcwallet=alice getnewaddress "" bech32; done

echo "# 3. 개인키 없는 지갑으로 가져오기 · timestamp 0 = 체인 처음부터 다시 훑기"
if ! $CLI listwallets | jq -e 'index("watch2")' > /dev/null; then
  $CLI -named createwallet wallet_name=watch2 disable_private_keys=true blank=true > /dev/null \
    || $CLI loadwallet watch2 > /dev/null
fi
$CLI -rpcwallet=watch2 importdescriptors \
  "[{\"desc\":\"$DESC\",\"active\":true,\"internal\":false,\"timestamp\":0}]"
$CLI -rpcwallet=watch2 getbalances

echo "# 4. 체크섬 실험: xpub 한 글자를 바꾸고 체크섬은 그대로 → getdescriptorinfo 오류"
BAD=$(python3 -c '
import sys; d = sys.argv[1]; i = d.index("pub") + 10
print(d[:i] + ("A" if d[i] != "A" else "B") + d[i + 1:])' "$DESC")
echo "BAD=$BAD"
$CLI getdescriptorinfo "$BAD" || echo "→ 예상대로 오류"
