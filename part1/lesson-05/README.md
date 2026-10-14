# lesson-05 · 2-1 Bitcoin Core 구조: 구성 프로그램, 데이터 디렉터리, 배포본 검증, 표준 설정

1부 기초 · 2강 Bitcoin Core 실습 환경

## 목표

- 구성 프로그램과 데이터 디렉터리 구조를 설명할 수 있다
- 공식 배포본의 해시와 서명을 검증한 뒤 설치할 수 있다
- 과정 실습용 bitcoin.conf를 작성하고 옵션을 설명할 수 있다

## 구성 프로그램

| 프로그램 | 역할 |
|---|---|
| `bitcoind` | 노드 본체(데몬). 검증·저장·전파·RPC 서버 |
| `bitcoin-cli` | bitcoind에 RPC 명령을 보내는 클라이언트 |
| `bitcoin-qt` | GUI가 붙은 노드 + 지갑 |
| `bitcoin-wallet` | 노드 없이 지갑 파일을 다루는 도구 |
| `bitcoin-tx` · `bitcoin-util` | 트랜잭션 조작·보조 도구 |

과정 기본 조합은 `bitcoind` + `bitcoin-cli`입니다.

## 데이터 디렉터리

```
~/.bitcoin/
  bitcoin.conf
  blocks/       블록 원본 (가장 큼)
  chainstate/   현재 UTXO 집합 (1-4)
  indexes/      txindex 등 선택 색인
  wallets/      지갑 파일
  regtest/ signet/ testnet4/
# macOS ~/Library/Application Support/Bitcoin
# Windows %LOCALAPPDATA%\Bitcoin
```

이 과정의 실습은 대부분 regtest에서 하므로 메인넷 동기화(약 770 GB, 2026-09 기준)는 필수가 아닙니다.

## 실습: 설치와 첫 실행 (약 20분)

| 단계 | 할 일 | 어디서 |
|---|---|---|
| 1 | 배포본(31.1), SHA256SUMS, .asc 받기 | [env/README.md §1](../../env/README.md) |
| 2 | 해시·서명 검증 결과를 캡처해 활동지에 첨부 | [env/README.md §1](../../env/README.md) |
| 3 | 설치 후 데이터 디렉터리에 bitcoin.conf 두기 | [env/README.md §2](../../env/README.md), [env/bitcoin.conf](../../env/bitcoin.conf) |
| 4 | regtest로 실행하고 응답 확인 | 아래 명령 |
| 5 | 종료했다가 다시 실행해 보기 | 아래 명령 |

1~2단계 명령:

```bash
sha256sum --ignore-missing \
  --check SHA256SUMS
git clone https://github.com/bitcoin-core/guix.sigs
gpg --import guix.sigs/builder-keys/*
gpg --verify SHA256SUMS.asc \
  SHA256SUMS
```

3단계(리눅스·WSL):

```bash
mkdir -p ~/.bitcoin && cp env/bitcoin.conf ~/.bitcoin/bitcoin.conf
```

4~5단계 슬라이드 명령:

```bash
bitcoind -regtest -daemon
bitcoin-cli -regtest \
  getblockchaininfo
bitcoin-cli -regtest stop
```

4~5단계를 한 번에(준비될 때까지 기다리는 부분 포함):

```bash
part1/lesson-05/lab.sh
```

## 기대 출력

1단계 해시 검증:

```
bitcoin-31.1-x86_64-linux-gnu.tar.gz: OK
```

2단계 서명 검증: 빌더마다 `gpg: Good signature from "..."`. 신뢰 서명을 하지 않은 키에는 `WARNING: This key is not certified with a trusted signature!`가 함께 나오는데 정상입니다. `BAD signature`가 나오면 설치하지 마세요.

4단계: `bitcoind -regtest -daemon`은 `Bitcoin Core starting`을 출력하고 바로 돌아옵니다. `getblockchaininfo` 응답에서 **`"chain": "regtest"`가 나오면 성공**입니다. 처음 실행한 regtest 노드라면 다음 값들이 나옵니다(일부 필드만 보임).

```
{
  "chain": "regtest",
  "blocks": 0,
  "headers": 0,
  "bestblockhash": "0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206",
  ...
}
```

`bestblockhash`는 regtest 제네시스 블록 해시로, 누구의 노드에서나 같습니다([lesson-02](../lesson-02/README.md)). 이미 블록을 만든 노드라면 `blocks`와 `bestblockhash`는 다릅니다.

5단계: `stop`은 `Bitcoin Core stopping`을 출력합니다. 다시 실행한 뒤:

```
{
  "chain": "regtest",
  "blocks": 0
}
```

다시 켜도 블록 수가 그대로인 것은 데이터가 `~/.bitcoin/regtest/` 아래 남아 있기 때문입니다.

## 흔히 막히는 지점

- **실행 직후 바로 명령을 보내 `error code: -28` (Loading block index… 등) 오류.** 노드가 아직 준비 중입니다. 몇 초 기다렸다가 다시 보내면 됩니다. `lab.sh`는 준비될 때까지 자동으로 기다립니다.
- **설정 파일을 데이터 디렉터리가 아닌 곳에 둠.** 적용되지 않습니다. 리눅스 `~/.bitcoin/bitcoin.conf`, macOS `~/Library/Application Support/Bitcoin/bitcoin.conf` 위치를 확인하세요. 이후 송금에서 `fallbackfee` 오류로 드러납니다.
- **이미 실행 중인데 `bitcoind -regtest -daemon`을 다시 실행.** 데이터 디렉터리 잠금 오류가 납니다. `bitcoin-cli -regtest stop` 후 다시 실행하세요.
- **`txindex=1`과 `prune`을 함께 설정.** 함께 쓸 수 없어 노드가 시작하지 않습니다.
- **Windows.** WSL을 권장합니다. 네이티브 설치는 배포 PDF를 참고하세요.

## 핵심 확인 질문

- 풀노드가 하는 세 가지 일(검증, 전파, 내 지갑 확인) 중 개인에게 가장 중요한 것은 무엇이고 왜인가요?
- 프루닝 노드가 할 수 없는 일은 무엇인가요?
- 배포본의 해시만 확인하고 서명을 확인하지 않으면 어떤 공격을 막지 못하나요?

## 퀴즈

[quiz/lesson-05.md](../../quiz/lesson-05.md)
