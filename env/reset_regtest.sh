#!/usr/bin/env bash
# regtest 실습 환경을 처음 상태로 되돌린다 (2-2).
# 지우는 것은 데이터 디렉터리 아래 regtest 폴더 하나뿐이다.
# bitcoin.conf, 메인넷·signet·testnet4 데이터는 건드리지 않는다.
#
# 데이터 디렉터리는 BITCOIN_DATADIR 환경변수로 바꿀 수 있다. 기본값은 ~/.bitcoin(리눅스).
#   macOS:  BITCOIN_DATADIR="$HOME/Library/Application Support/Bitcoin" env/reset_regtest.sh
#   Windows: WSL 안에서 실행하면 리눅스와 같다.
# 초기화한 뒤에는 env/setup_regtest.sh로 표준 환경을 다시 만든다.
set -euo pipefail

DATADIR="${BITCOIN_DATADIR:-$HOME/.bitcoin}"
DATADIR="${DATADIR%/}"
TARGET="$DATADIR/regtest"
CLI=(bitcoin-cli -regtest "-datadir=$DATADIR")

# 안전장치: 지울 경로는 반드시 '<데이터 디렉터리>/regtest' 형태여야 한다.
if [ -z "$DATADIR" ] || [ "$DATADIR" = "/" ] || [ "$DATADIR" = "$HOME" ]; then
  echo "중단: 데이터 디렉터리 값이 이상합니다: '$DATADIR'" >&2
  exit 1
fi
if [ "$(basename "$TARGET")" != "regtest" ]; then
  echo "중단: regtest 폴더가 아닌 경로는 지우지 않습니다: $TARGET" >&2
  exit 1
fi
if [ ! -d "$TARGET" ]; then
  echo "지울 regtest 폴더가 없습니다: $TARGET"
  echo "이미 초기 상태입니다. env/setup_regtest.sh로 환경을 만드세요."
  exit 0
fi

echo "다음 폴더를 통째로 지웁니다(블록, 지갑 miner·alice·bob 포함):"
echo "  $TARGET"
read -r -p "계속할까요? [y/N] " ANSWER || ANSWER=""
case "$ANSWER" in
  y|Y|yes|YES) ;;
  *) echo "취소했습니다. 아무것도 지우지 않았습니다."; exit 0 ;;
esac

# 노드가 실행 중이면 먼저 정지하고, 완전히 내려갈 때까지 기다린다.
if "${CLI[@]}" getblockchaininfo >/dev/null 2>&1; then
  echo "regtest 노드를 정지합니다..."
  "${CLI[@]}" stop >/dev/null
  for _ in $(seq 1 60); do
    if ! "${CLI[@]}" getblockchaininfo >/dev/null 2>&1 \
       && [ ! -e "$TARGET/bitcoind.pid" ]; then
      break
    fi
    sleep 1
  done
  if "${CLI[@]}" getblockchaininfo >/dev/null 2>&1; then
    echo "중단: 노드가 60초 안에 멈추지 않았습니다. 다시 시도하세요." >&2
    exit 1
  fi
  sleep 1
fi

rm -rf -- "$TARGET"
echo "삭제 완료: $TARGET"
echo "다음: env/setup_regtest.sh"
