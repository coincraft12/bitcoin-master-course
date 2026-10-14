# lesson-06 · 2-2 네트워크 모드: mainnet·testnet4·signet·regtest와 과정 표준 환경

1부 기초 · 2강 Bitcoin Core 실습 환경

## 목표

- mainnet, testnet4, signet, regtest의 차이와 용도를 설명할 수 있다
- 주소 접두어로 네트워크를 구분할 수 있다
- 과정 표준 regtest 환경을 스크립트로 구성할 수 있다

## 네 개의 네트워크

| 네트워크 | 용도 | 블록 생성 | 코인 얻는 법 | P2P / RPC 포트 | 주소 접두어 |
|---|---|---|---|---|---|
| mainnet | 실제 운영 | 작업증명 경쟁 | 구매·채굴 | 8333 / 8332 | `bc1` (레거시 `1`, `3`) |
| testnet4 | 공개 테스트 | 작업증명(낮은 난이도) | 파우셋 | 48333 / 48332 | `tb1` (레거시 `m`·`n`, `2`) |
| signet | 안정적 공개 테스트 | 지정 서명자가 서명한 블록만 유효 | 파우셋 | 38333 / 38332 | `tb1` (레거시 `m`·`n`, `2`) |
| regtest | 개인 실험실 | 명령 한 줄로 즉시 생성 | 직접 채굴 | 18444 / 18443 | `bcrt1` (레거시 `m`·`n`, `2`) |

- testnet4는 v28부터. `-testnet4`로 실행합니다(`-testnet`은 사용 중단 예고된 testnet3).
- regtest는 150블록마다 반감기가 옵니다(11-2 발행 실습).

## 성숙 규칙: 채굴 보상은 100블록 뒤에 쓸 수 있다

블록 1의 코인베이스 출력 50 BTC는 지갑에 immature로 표시되고, 그 위에 100블록이 더 쌓여 블록 101이 만들어진 뒤에야 처음으로 쓸 수 있습니다. 그래서 regtest에서는 처음에 101블록을 만듭니다.

## 실습: 성숙 규칙을 손으로 확인하기

| 단계 | 할 일 |
|---|---|
| 1 | 블록 1개 뒤 잔액 0, immature 항목 확인 |
| 2 | 100블록 더 만들고 50 BTC 확인 |
| 3 | `setup_regtest.sh`로 표준 환경 구성 |
| + | 선택: signet 접속, 파우셋에서 소액 받기 |

처음 상태의 노드에서 하세요. 이미 블록이 있으면 `env/reset_regtest.sh`로 초기화한 뒤 `bitcoind -regtest -daemon`으로 다시 띄웁니다.

### 1~2단계: 손으로 먼저

```bash
# 스크립트 전에 손으로 먼저
CLI="bitcoin-cli -regtest"; $CLI createwallet test
A=$($CLI -rpcwallet=test getnewaddress)
$CLI generatetoaddress 1 $A;   $CLI -rpcwallet=test getbalances   # immature 50
$CLI generatetoaddress 100 $A; $CLI -rpcwallet=test getbalance    # 50.00000000
```

한 줄씩 터미널에 쳐 보길 권합니다. 같은 내용이 `part1/lesson-06/lab.sh`에 있습니다. 블록 1개 뒤 `getbalance`도 직접 쳐서 0인지 확인하세요.

```bash
$CLI -rpcwallet=test getbalance    # 블록 1개 뒤: 0.00000000
```

### 3단계: 표준 환경

```bash
env/setup_regtest.sh
```

`setup_regtest.sh`의 동작과 기대 출력은 [env/README.md](../../env/README.md)에 있습니다. 1~2단계를 한 뒤에 실행하면 블록이 이미 101개라 슬라이드의 채굴 조건(`getblockcount`가 101 미만)을 건너뛰지만, 저장소 스크립트는 miner 잔액이 모자라면 miner에게 101블록을 더 채굴해서 계속 진행합니다(ERRATA.md 참고).

## 기대 출력

처음 상태에서 실행한 예(블록 해시·주소는 실행마다 다름):

```
{
  "name": "test"
}
[
  "18f725344cb25774c277bb6c7cf63a138a4ed041de94507232aa8cc6e6098a23"
]
{
  "mine": {
    "trusted": 0.00000000,
    "untrusted_pending": 0.00000000,
    "immature": 50.00000000
  },
  "lastprocessedblock": {
    "hash": "18f725344cb25774c277bb6c7cf63a138a4ed041de94507232aa8cc6e6098a23",
    "height": 1
  }
}
[
  "...(블록 해시 100개)..."
]
50.00000000
```

- 블록 1개 뒤: `getbalance`는 0, `getbalances`의 `immature`에 50 BTC. 보상은 생겼지만 아직 쓸 수 없습니다.
- 100블록 더 만든 뒤: `getbalance`가 50 BTC. 블록 101이 만들어지면서 첫 보상이 성숙했습니다. 블록 2~101의 보상은 아직 immature입니다.

3단계 뒤에는 `alice: 5.00000000 BTC`, `bob: 5.00000000 BTC`가 출력되어야 합니다.

## 선택: signet 접속

```bash
bitcoind -signet -daemon
bitcoin-cli -signet getblockchaininfo | jq '{chain, blocks, headers, verificationprogress}'
bitcoin-cli -signet createwallet signet-test
bitcoin-cli -signet -rpcwallet=signet-test getnewaddress     # tb1로 시작
```

`verificationprogress`가 1에 가까워지면 동기화가 끝난 것입니다. 받은 `tb1` 주소를 signet 파우셋에 넣어 소액을 받아 봅니다. regtest 노드와 동시에 띄워도 됩니다(데이터 하위 폴더와 포트가 다름). 끝나면 `bitcoin-cli -signet stop`.

## 흔히 막히는 지점

- **`getbalance`와 `getbalances`를 헷갈림.** 끝에 s가 붙은 `getbalances`가 trusted, immature 같은 항목별 잔액을 나눠 보여 줍니다.
- **100블록만 만들고 잔액이 0이라 당황.** 블록 1의 보상은 블록 101이 생겨야 씁니다. 블록을 하나 더 만드세요.
- **`createwallet test`가 "Database already exists" 오류.** 이전에 만든 test 지갑이 있습니다. `$CLI loadwallet test`로 불러오거나, `env/reset_regtest.sh`로 처음부터 다시 하세요.
- **실습 캡처에 `bc1` 주소가 섞임.** 메인넷 주소입니다. 접두어를 보고 확인하는 습관을 들이세요.

## 퀴즈

[quiz/lesson-06.md](../../quiz/lesson-06.md)
