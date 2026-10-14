# lesson-02 · 1-2 백서 다시 읽기: 12개 절과 지금의 차이

1부 기초 · 1강 비트코인 개요와 동작 원리

## 목표

- 백서 12개 절의 구조를 한 문장씩 요약할 수 있다
- 제네시스 블록을 노드에서 직접 확인할 수 있다
- 백서와 현재 구현의 차이를 세 가지 이상 말할 수 있다

## 준비

- regtest 노드가 실행 중이어야 합니다. 노드 환경은 2강([lesson-05](../lesson-05/README.md), [lesson-06](../lesson-06/README.md))에서 만듭니다. 아직 환경이 없다면 공개 탐색기에서 메인넷 블록 0을 열어 같은 순서로 진행해도 됩니다.
- `jq`가 설치되어 있어야 합니다(`jq --version`). 없으면 둘째 줄이 실패합니다.

## 실습: 내 노드에서 제네시스 블록 보기

regtest의 제네시스 블록은 메인넷과 **블록 해시가 다르지만 코인베이스 트랜잭션은 같습니다.** 그래서 regtest 노드로도 헤드라인 문구를 꺼낼 수 있습니다.

| 단계 | 할 일 |
|---|---|
| 1 | 블록 0의 코인베이스 입력을 꺼낸다 |
| 2 | 바이트를 문자로 출력해 헤드라인 문구를 찾는다 |
| 3 | 메인넷 제네시스 해시와 비교하고, 다른 이유를 설명한다 |

슬라이드 명령(1~2단계):

```bash
# regtest도 메인넷과 같은 제네시스 코인베이스를 갖는다
H0=$(bitcoin-cli -regtest getblockhash 0)
bitcoin-cli -regtest getblock $H0 2 | jq -r '.tx[0].vin[0].coinbase' > genesis_cb.hex
python3 -c "print(bytes.fromhex(open('genesis_cb.hex').read().strip()))"
```

세 단계를 한 번에 하려면:

```bash
part1/lesson-02/lab.sh
```

`genesis_cb.hex`는 실행한 폴더(저장소 최상위)에 생깁니다.

## 기대 출력

아래 값은 모두 결정적입니다(어느 컴퓨터에서 실행해도 같음).

`genesis_cb.hex` 내용:

```
04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73
```

2단계 출력:

```
b'\x04\xff\xff\x00\x1d\x01\x04EThe Times 03/Jan/2009 Chancellor on brink of second bailout for banks'
```

읽을 수 있는 문자열 `The Times 03/Jan/2009 Chancellor on brink of second bailout for banks`가 헤드라인입니다. 앞의 몇 바이트(`04 ffff001d`, `01 04`, `45`)는 난이도 값 같은 다른 데이터와 길이 바이트입니다.

3단계 출력:

```
regtest 블록 0 해시: 0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206
mainnet 블록 0 해시: 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
---- regtest 블록 0 헤더 (time, nonce, bits, merkleroot) ----
{
  "time": 1296688602,
  "nonce": 2,
  "bits": "207fffff",
  "merkleroot": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
}
```

### 해시가 다른 이유

머클 루트(코인베이스가 같으니 같음)는 그대로이고, 헤더의 시간·논스·난이도가 다릅니다.

| 헤더 필드 | mainnet | regtest |
|---|---|---|
| time | 1231006505 (2009-01-03) | 1296688602 |
| nonce | 2083236893 | 2 |
| bits | 1d00ffff | 207fffff |
| merkleroot | 4a5e1e4b…a33b | 4a5e1e4b…a33b (같음) |

블록 해시는 이 헤더 전체의 이중 SHA256이므로, 필드 하나만 달라도 해시가 완전히 달라집니다. regtest는 난이도가 매우 낮아(bits 207fffff) 논스 2에서 바로 조건을 만족했습니다.

## 흔히 막히는 지점

- **`jq: command not found`**: 둘째 줄이 실패합니다. `sudo apt install jq`(리눅스·WSL), `brew install jq`(macOS)로 미리 설치하세요.
- **`Could not connect to the server`**: 노드가 꺼져 있습니다. `bitcoind -regtest -daemon` 후 몇 초 기다립니다.
- **제네시스 블록의 50 BTC를 찾으려는 경우**: 그 출력은 UTXO 집합에 추가되지 않아 누구도 쓸 수 없습니다. `gettxout`으로 조회해도 나오지 않습니다.

## 핵심 확인 질문

- 백서 12개 절을 각각 한 문장으로 요약하고, 과정의 어느 차시와 연결되는지 말해 보세요(1-2 WHITEPAPER MAP).
- 제네시스 블록의 네 가지 특징(이전 해시 0, 신문 헤드라인, 쓸 수 없는 50 BTC, chainparams 하드코딩)은 각각 왜 중요한가요?
- 백서(2008)와 현재(2026)의 차이를 세 가지 이상 말해 보세요. 예: 가장 긴 체인 → 누적 작업량이 가장 큰 체인(10-3), 서명이 SegWit으로 분리(5-2·6-4·7-3), 실제 규칙은 Bitcoin Core 구현과 BIP(11-4).

## 퀴즈

[quiz/lesson-02.md](../../quiz/lesson-02.md)
