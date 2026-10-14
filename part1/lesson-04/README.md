# lesson-04 · 1-4 UTXO 모델: 잔액이 아니라 코인이 있다

1부 기초 · 1강 비트코인 개요와 동작 원리

## 목표

- UTXO 모델에서 코인과 잔액이 무엇인지 설명할 수 있다
- 트랜잭션이 UTXO 집합을 바꾸는 과정을 그릴 수 있다
- 이더리움의 계정 모델과 비교할 수 있다

## UTXO의 세 가지 규칙

1. 입력은 이전 출력을 가리키고 소비한다
2. 출력은 한 번만, 통째로 소비된다
3. 입력 합 − 출력 합 = 수수료

- **잔액** = 내 키로 열 수 있는 UTXO의 합. 그래서 같은 키를 어느 지갑 앱에 넣어도 같은 잔액이 보인다.
- **chainstate**: 노드는 남은 UTXO 전체를 관리한다. 입력이 가리키는 출력이 여기 없으면 이중지불이다.

예: 철수의 UTXO 0.5 BTC, 0.3 BTC 중 0.5 BTC를 입력으로 영희에게 0.2 BTC, 잔돈 0.2999 BTC → 수수료 0.0001 BTC. 송금 후 철수의 잔액 = 0.3 + 0.2999 = 0.5999 BTC. 어디에도 저장되지 않고, 지갑이 더한 값입니다.

## 실습 A (슬라이드 LAB): 잔액을 UTXO로 해체하기 — 공개 탐색기

| 단계 | 할 일 |
|---|---|
| 1 | 거래가 많은 공개 주소 하나를 탐색기로 조회한다 |
| 2 | 표시된 잔액과 미사용 출력의 합계를 비교한다 |
| 3 | 사용된 출력 하나가 어느 트랜잭션에서 소비됐는지 따라간다 |

## 실습 B: 2강 이후, 내 노드에서 같은 실습 반복

표준 환경([env/README.md](../../env/README.md))이 있어야 합니다.

### B-1. 슬라이드 명령

```bash
bitcoin-cli -regtest gettxoutsetinfo | jq '{txouts, total_amount}'
bitcoin-cli -regtest -rpcwallet=alice listunspent
bitcoin-cli -regtest -rpcwallet=alice getbalance
bitcoin-cli -regtest scantxoutset start '["addr(<alice 주소>)"]'
```

`<alice 주소>`는 꺾쇠까지 지우고 실제 alice 주소로 바꿔 넣습니다. `lab.sh`는 `listunspent` 첫 항목의 주소를 자동으로 채워 네 명령을 실행합니다.

```bash
part1/lesson-04/lab.sh
```

| 명령 | 보는 것 |
|---|---|
| `gettxoutsetinfo` | 노드가 관리하는 UTXO 집합 전체 요약(출력 개수, 총액) |
| `listunspent` | alice 지갑의 UTXO 목록 |
| `getbalance` | alice 지갑의 잔액 |
| `scantxoutset` | 지갑 없이 UTXO 집합에서 주어진 주소의 출력을 직접 찾기 |

기대 출력(새로 만든 표준 환경 직후의 예. txid·주소·해시·출력 개수는 실행마다 다름):

```
{
  "txouts": 104,
  "total_amount": 5100.00000000
}
[
  {
    "txid": "77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9",
    "vout": 0,
    "address": "bcrt1qhy8uq2dm8kgp67umwzwsnehgy7k634xjsyz2ud",
    "label": "",
    "scriptPubKey": "0014...",
    "amount": 5.00000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([...]...)#...",
    "parent_descs": [ "..." ],
    "safe": true
  }
]
5.00000000
{
  "success": true,
  "txouts": 104,
  "height": 102,
  "bestblock": "1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c",
  "unspents": [
    {
      "txid": "77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9",
      "vout": 0,
      "scriptPubKey": "0014...",
      "desc": "addr(bcrt1qhy8uq2dm8kgp67umwzwsnehgy7k634xjsyz2ud)#...",
      "amount": 5.00000000,
      "coinbase": false,
      "height": 102,
      "blockhash": "1ded3b1e2b5db009d9bc51a47aced0ef8223364c14f6b09e17e0210e8653135c",
      "confirmations": 1
    }
  ],
  "total_amount": 5.00000000
}
```

(`...`로 줄인 필드는 길어서 생략. 모든 값은 실행마다 다름)

표준 환경 직후 alice의 UTXO는 miner가 보낸 5 BTC 하나이므로 `listunspent` 합계 = `getbalance` = 5 BTC입니다.

### B-2. UTXO 합 = 잔액을 코드로 확인

```bash
python part1/lesson-04/utxo_balance.py          # 기본 alice
python part1/lesson-04/utxo_balance.py bob
```

기대 출력(새 표준 환경 직후의 예. txid는 실행마다 다름):

```
alice 지갑의 UTXO 1개
  77a1a82ba10a33c3611222680d56ffda7c9df9494fe3ca07069e44f337c712f9:0  확인   1     500000000 sat
UTXO 합계  : 500000000 sat = 5.00000000 BTC
getbalance : 500000000 sat = 5.00000000 BTC
일치
```

[lesson-03](../lesson-03/README.md)의 `lab.sh`를 먼저 돌렸다면 alice의 UTXO는 잔돈 하나(약 4.9 BTC)로 바뀌어 있고, 합계와 잔액은 여전히 일치합니다. 원래 5 BTC 출력은 소비되어 집합에서 사라졌기 때문입니다.

`utxo_balance.py`는 `listunspent(0)`으로 미확정 출력까지 받은 뒤 `safe`가 거짓인 것(남이 보낸 미확정 출력)만 뺍니다. `getbalance`가 세는 범위와 맞추기 위해서입니다. 금액은 `btc_to_sat`으로 sat 정수로 바꿔 더합니다(2-4).

## 흔히 막히는 지점

- **꺾쇠 표시 `<alice 주소>`를 그대로 두고 실행.** 실제 alice 주소로 바꿔 넣으세요.
- **`listunspent` 합계가 `getbalance`보다 작음.** `listunspent`는 기본으로 1 확인 이상만 보여 줍니다. 방금 송금해서 잔돈이 미확정이면 빠집니다. `bitcoin-cli -regtest -rpcwallet=miner -generate 1`로 블록을 만든 뒤 다시 보거나, `listunspent 0`으로 봅니다.
- **`scantxoutset`이 오래 걸리거나 "Scan already in progress".** 한 번에 하나의 스캔만 됩니다. 끝날 때까지 기다리세요.

## 비트코인 UTXO와 이더리움 계정

| 항목 | 비트코인 UTXO | 이더리움 계정 |
|---|---|---|
| 상태 | 쓰지 않은 출력들의 집합 | 계정별 잔액·논스·저장소 |
| 송금 | 코인을 소비하고 새 코인을 만든다 | 잔액 숫자를 빼고 더한다 |
| 이중지불 방지 | 출력이 이미 소비되었는지 확인 | 계정 논스로 순서를 강제 |
| 병렬 검증 | 입력 단위로 독립 검증이 쉽다 | 같은 계정의 거래는 순서 의존 |
| 프라이버시 | 매번 새 주소·잔돈 주소를 쓸 수 있다 | 한 계정에 활동이 모인다 |
| 프로그래밍 | 출력 단위의 잠금 조건 (6강) | 상태를 읽고 쓰는 컨트랙트 |

## 핵심 확인 질문

- 블록체인 어디에도 잔액이 없는데 지갑은 잔액을 어떻게 보여 주나요?
- 1 BTC짜리 UTXO 하나로 0.1 BTC를 보내면 어떤 출력이 생기나요? 잔돈 출력을 빠뜨리면 무슨 일이 생기나요?
- 노드는 이중지불을 어떻게 걸러 내나요?

## 퀴즈

[quiz/lesson-04.md](../../quiz/lesson-04.md)
