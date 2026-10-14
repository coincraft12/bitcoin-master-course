#!/usr/bin/env bash
# 6강 미니 과제 02 정답 예: 디스크립터 체크섬을 Core getdescriptorinfo로 검증하고 주소를 대조. 저장소 최상위에서 실행.
#   bash part3/lesson-27/assignment/solution/check_with_core.sh
set -euo pipefail
CLI="bitcoin-cli -regtest"
DESC=$(python3 part3/lesson-27/assignment/solution/solution_inheritance.py --desc)
echo "DESC=$DESC"
$CLI getdescriptorinfo "$DESC" | jq -c '{checksum, isrange, issolvable, hasprivatekeys}'
echo "Core 주소 : $($CLI deriveaddresses "$DESC" | jq -r '.[0]')"
echo "내 계산   : $(python3 part3/lesson-27/assignment/solution/solution_inheritance.py | grep '주소' | cut -d' ' -f3)"
