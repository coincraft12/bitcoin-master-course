#!/usr/bin/env bash
# 11-5 실습 ①: 지금 노드의 배포 상태 (s115-lab1). 저장소 최상위에서 실행.
#   bash part4/lesson-48/deployments.sh
set -euo pipefail
bitcoin-cli --version | head -1
bitcoin-cli -regtest getdeploymentinfo | jq '.deployments | to_entries[]
  | {name: .key, type: .value.type, active: .value.active, height: .value.height}'
# Core 32부터 taproot 항목이 빠진다(릴리스 노트 초안) → Taproot 지원은 "항상 활성"으로 가정하거나
# Core 31부터 있는 script_flags의 TAPROOT로 확인한다.
echo "# script_flags (Core 31~)"
bitcoin-cli -regtest getdeploymentinfo \
  | jq -c '.script_flags // "script_flags 필드가 없다 → bitcoin-cli help getdeploymentinfo 로 위치 확인"'
