#!/usr/bin/env bash
# 10-4 실습: 동기화 관찰과 UTXO 스냅샷 (s104-lab). 저장소 최상위에서 실행.
#   bash part4/lesson-43/sync_snapshot.sh
# signet 부분은 signet 노드가 떠 있을 때만, regtest 부분은 regtest 노드가 필요하다. jq 필요.
set -uo pipefail

if bitcoin-cli -signet getblockchaininfo >/dev/null 2>&1; then
# signet 노드: 헤더가 먼저 최신 높이에 (헤더 우선)
bitcoin-cli -signet getblockchaininfo | jq '{blocks, headers, verificationprogress, initialblockdownload}'
grep UpdateTip ~/.bitcoin/signet/debug.log | tail -3
else
  echo "(signet 노드 없음 → signet 부분 건너뜀. 띄우려면 bitcoind -signet -daemon)"
fi

# regtest: UTXO 집합 전체를 파일 하나로
bitcoin-cli -regtest gettxoutsetinfo | jq '{height, txouts, total_amount, hash_serialized_3}'
rm -f /tmp/utxo_snapshot.dat          # (저장소 보탬) 이미 있으면 dumptxoutset이 실패한다
bitcoin-cli -regtest dumptxoutset /tmp/utxo_snapshot.dat latest
ls -lh /tmp/utxo_snapshot.dat

echo "# 우리 regtest 체인은 소스에 등록된 스냅샷 높이·해시와 달라 loadtxoutset이 실패한다 → 그 실패가 바로 안전장치"
bitcoin-cli -regtest loadtxoutset /tmp/utxo_snapshot.dat || echo "→ 예상대로 실패"
