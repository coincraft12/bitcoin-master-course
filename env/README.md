# env/ — 과정 표준 실습 환경

과정의 모든 실습은 같은 출발점에서 시작합니다(2-2).

| 구성 | 상태 |
|---|---|
| 노드 | `bitcoind -regtest` 실행 중 |
| `miner` | 블록 채굴과 자금 공급. 성숙한 코인을 충분히 보유 |
| `alice` | 보내는 사람. 실습 자금 5 BTC로 시작 |
| `bob` | 받는 사람. 실습 자금 5 BTC로 시작 |

| 파일 | 내용 |
|---|---|
| `bitcoin.conf` | 과정 표준 설정 파일(2-1). 데이터 디렉터리에 복사해서 쓴다 |
| `setup_regtest.sh` | 노드 실행, 지갑 3개 준비, 101블록 채굴, alice·bob에게 5 BTC씩 지급, 세 지갑 잔액 출력(2-2) |
| `reset_regtest.sh` | regtest 폴더만 지워 처음 상태로 되돌림. 실행 전에 확인을 묻고, 노드를 정지한 뒤 삭제(2-2) |

기준 버전: Bitcoin Core 31.1 (2026년 10월 현재 최신 배포본).

---

## 1. 설치 전에 배포본부터 검증한다 (2-1)

노드 프로그램이 변조되면 그 노드가 하는 모든 검증이 무의미해집니다. 공식 사이트 `https://bitcoincore.org/bin/bitcoin-core-31.1/` 에서 세 가지를 같은 폴더에 받습니다.

- 운영체제에 맞는 배포본 (예: `bitcoin-31.1-x86_64-linux-gnu.tar.gz`)
- `SHA256SUMS`
- `SHA256SUMS.asc` (서명 파일)

### STEP 1 · 해시: 받은 파일이 목록과 같은가

```bash
sha256sum --ignore-missing \
  --check SHA256SUMS
```

`--ignore-missing`을 주면 목록에는 있지만 내려받지 않은 다른 운영체제용 파일은 건너뛰고, 내가 받은 파일만 검사합니다.

기대 출력:

```
bitcoin-31.1-x86_64-linux-gnu.tar.gz: OK
```

- macOS: `shasum -a 256 bitcoin-31.1-arm64-apple-darwin.tar.gz` 로 해시를 구해 `grep bitcoin-31.1-arm64-apple-darwin.tar.gz SHA256SUMS` 의 값과 비교
- Windows: `certUtil -hashfile bitcoin-31.1-win64-setup.exe SHA256` 으로 해시를 구해 `SHA256SUMS`의 같은 파일 줄과 눈으로 비교

### STEP 2 · 서명: 목록 자체를 누가 서명했나

해시 목록이 바꿔치기되었다면 1단계는 소용없습니다. 여러 독립 빌더가 재현 가능한 빌드로 같은 결과물을 만들고 각자 PGP로 서명합니다. 빌더 공개키는 `bitcoin-core/guix.sigs` 저장소의 `builder-keys` 폴더에 모여 있습니다.

```bash
git clone https://github.com/bitcoin-core/guix.sigs
gpg --import guix.sigs/builder-keys/*
gpg --verify SHA256SUMS.asc \
  SHA256SUMS
```

기대 출력: 빌더마다 `gpg: Good signature from "..."` 줄이 나옵니다. 각 빌더 키를 직접 인증(신뢰 서명)하지 않았다면 `WARNING: This key is not certified with a trusted signature!` 경고가 함께 나오는데, 이는 "이 키가 그 사람의 것인지 당신이 직접 확인하지 않았다"는 뜻일 뿐 서명이 틀렸다는 뜻이 아닙니다. `BAD signature`가 하나라도 나오면 설치하지 마세요.

STEP 1의 `OK` 메시지와 STEP 2의 `Good signature` 메시지를 캡처해 활동지에 첨부합니다(2-1 LAB 2단계). 이 절차의 의미는 12-1 공급망 공격에서 다시 다룹니다.

### 설치

리눅스(WSL 포함) 예:

```bash
tar xzf bitcoin-31.1-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-31.1/bin/*
bitcoind -version | head -1
```

Windows는 WSL을 권장합니다. 네이티브 설치 안내는 배포 PDF에 있습니다. GUI를 쓰는 분은 `bitcoin-qt`의 콘솔 창에서 같은 RPC 명령을 쓸 수 있습니다.

---

## 2. bitcoin.conf를 데이터 디렉터리에 둔다 (2-1)

| 운영체제 | 데이터 디렉터리 |
|---|---|
| 리눅스 | `~/.bitcoin/` |
| macOS | `~/Library/Application Support/Bitcoin/` |
| Windows | `%LOCALAPPDATA%\Bitcoin\` |

```bash
mkdir -p ~/.bitcoin
cp env/bitcoin.conf ~/.bitcoin/bitcoin.conf
# macOS
# mkdir -p "$HOME/Library/Application Support/Bitcoin"
# cp env/bitcoin.conf "$HOME/Library/Application Support/Bitcoin/bitcoin.conf"
```

`[regtest]` 섹션의 `fallbackfee`가 가장 중요합니다. regtest에는 수수료 추정 데이터가 없어서, 이 줄이 없으면 `sendtoaddress`가 수수료 추정 실패 오류를 냅니다. 송금이 안 되면 가장 먼저 이 줄을 확인하세요. `txindex=1`은 프루닝(`prune`)과 함께 쓸 수 없습니다.

---

## 3. 데이터 디렉터리 지정: BITCOIN_DATADIR

`lib/rpc.py`와 `reset_regtest.sh`는 쿠키 파일과 regtest 폴더를 찾을 때 `BITCOIN_DATADIR` 환경변수를 읽습니다. 없으면 `~/.bitcoin`(리눅스 기본값)을 씁니다. **macOS는 반드시 지정하세요.**

```bash
# macOS: ~/.zshrc 등에 넣어 두면 편하다
export BITCOIN_DATADIR="$HOME/Library/Application Support/Bitcoin"
```

`bitcoind`와 `bitcoin-cli`는 이 변수를 읽지 않고 운영체제 기본 위치를 씁니다. 그래서 `setup_regtest.sh`도 기본 위치를 씁니다. `BITCOIN_DATADIR`은 그 기본 위치를 Python 코드와 reset 스크립트에 알려 주는 용도입니다.

---

## 4. 사용법

모든 명령은 저장소 최상위(`bitcoin-master-course/`)에서 실행합니다.

### 표준 환경 만들기

```bash
env/setup_regtest.sh
```

기대 출력(처음 실행하면 맨 앞에 `generatetoaddress 101`이 만든 블록 해시 101개가 JSON 배열로 나오고, 이어서 miner → alice, miner → bob 송금 txid가 나온다. txid·주소·블록 해시·miner 잔액은 실행마다 다름):

```
[
  "cf1238aa4d756ee2f5235d02833b9d35e6456ab7a1d57b72057385fe23206f53",
  ...(블록 해시 101개)...
]
77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9
bed0f1f16a393be66c9dc2f2286efd831481109f2b1dfe9106f834041d5011da
{
  "address": "bcrt1qk22v2ucuf0d4p5sslwxpc3x4ct23de6uafecev",
  "blocks": [
    "1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c"
  ]
}
---- 지갑 잔액 (블록 높이 102) ----
miner: 89.99994360 BTC
alice: 5.00000000 BTC
bob: 5.00000000 BTC
```

새 환경에서 처음 실행하면 블록 높이는 102, alice와 bob은 5 BTC씩입니다. miner 잔액은 블록 1 보상 50 BTC에서 10 BTC와 두 송금의 수수료를 뺀 잔돈에, 블록 102가 쌓이면서 성숙한 블록 2의 보상 50 BTC를 더한 값입니다(수수료는 실행 환경에 따라 다름). 블록 3~102의 보상은 아직 미성숙이라 잔액에 들어가지 않습니다.

- 이미 있는 지갑은 불러오고, 블록이 101개 미만일 때만 채굴하므로 여러 번 실행해도 안전합니다.
- 송금 부분은 매번 다시 돌기 때문에, 다시 실행하면 alice와 bob의 잔액이 5 BTC씩 늘어납니다. 정상입니다. 정확히 5 BTC에서 시작하고 싶으면 먼저 초기화하세요.

### 처음 상태로 되돌리기

```bash
env/reset_regtest.sh
env/setup_regtest.sh
```

```
다음 폴더를 통째로 지웁니다(블록, 지갑 miner·alice·bob 포함):
  /home/you/.bitcoin/regtest
계속할까요? [y/N] y
regtest 노드를 정지합니다...
삭제 완료: /home/you/.bitcoin/regtest
다음: env/setup_regtest.sh
```

`reset_regtest.sh`는 `<데이터 디렉터리>/regtest` 폴더만 지우도록 경로가 고정되어 있습니다. `bitcoin.conf`와 메인넷·signet·testnet4 데이터는 건드리지 않습니다. `y`가 아닌 답을 하면 아무것도 지우지 않습니다.

### 노드 정지

```bash
bitcoin-cli -regtest stop
```

---

## 흔히 막히는 지점

| 증상 | 원인과 해결 |
|---|---|
| `sendtoaddress`가 수수료 추정 실패 오류 | `bitcoin.conf`의 `[regtest]` 아래 `fallbackfee=0.0002`가 없거나, 설정 파일이 데이터 디렉터리가 아닌 곳에 있음 |
| 실행 직후 `error code: -28` (Loading/Verifying ...) | 노드가 아직 준비 중. 몇 초 기다렸다가 다시 보낸다. `setup_regtest.sh`는 준비될 때까지 자동으로 기다린다 |
| `Could not connect to the server 127.0.0.1:18443` | `bitcoind`가 꺼져 있음. `bitcoind -regtest -daemon` |
| Python에서 `쿠키 파일이 없습니다` | 노드가 꺼져 있거나 `BITCOIN_DATADIR`이 실제 데이터 디렉터리와 다름(macOS) |
| `bitcoin-cli: command not found` | 설치한 `bin/` 폴더가 `PATH`에 없음 |
| 지갑 명령에서 지갑을 정할 수 없다는 오류 | 지갑이 여러 개 로드되어 있으면 `-rpcwallet=alice`처럼 대상을 지정해야 함(2-3) |
