# lesson-19 · 5-1 입력과 출력: outpoint, 금액, 수수료, 코인베이스

## 목표
- 트랜잭션의 최상위 필드(version · vin · vout · locktime)와 입력·출력 필드를 설명한다.
- raw 트랜잭션을 디코딩해 이전 출력을 거슬러 올라간다.
- 수수료가 어디에도 적혀 있지 않은 이유(수수료 = 입력 합 − 출력 합)를 설명한다.

## 실습 순서
1. **LAB ① (s51-lab1)** 블록 170, 사토시가 할 피니에게 보낸 첫 P2P 송금을 연다. txindex=1 메인넷 노드가 있으면 `getrawtransaction`, 없으면 저장소의 `data/T-02.hex`를 regtest `decoderawtransaction`에 넣는다(디코딩은 체인과 무관해 결과가 같다).
2. 확인할 것 세 가지: vin 1개(txid `0437cd7f…a597c9`, vout 0) · vout 2개(10 BTC → 할 피니, 40 BTC → 사토시 자신 = 잔돈) · 두 출력 모두 유형 `pubkey`(P2PK).
3. **LAB ② (s51-lab2)** 입력이 가리키는 `0437cd7f…`를 조회한다 → 블록 9의 코인베이스(vin의 txid가 0, 출력 0번 50 BTC). 수수료 = 50 − (10 + 40) = 0.
4. 선택 과제: `getrawtransaction … true` 출력에 `fee` 필드가 있는지 보고, 있다면 노드가 어떻게 계산했는지 설명한다(힌트: 수수료 공식, 이전 출력 조회).

## 실행 (저장소 최상위에서)
```bash
bash   part3/lesson-19/block170_lab.sh            # regtest 노드만 있어도 됨 (data/T-02.hex 디코딩)
bash   part3/lesson-19/block170_lab.sh mainnet    # txindex=1 메인넷 노드
python part3/lesson-19/trace_back.py              # 노드 없이 같은 확인 (lib/tx.py의 parse_tx를 미리 사용)
```

## 기대 출력
`trace_back.py` (결정적, 직접 실행한 값)
```
① 블록 170 송금 txid f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
   vin 1개
     txid 0437cd7f…a597c9, vout 0
   vout 2개
     0: 1,000,000,000 sat = 10 BTC · 유형 pubkey (P2PK: 공개키를 직접 잠금에)
     1: 4,000,000,000 sat = 40 BTC · 유형 pubkey (P2PK: 공개키를 직접 잠금에)

② 입력이 가리키는 이전 트랜잭션 0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9
   코인베이스인가: txid가 0으로 채워짐 True, vout 0xffffffff
   scriptSig(채굴자 임의 데이터) 04ffff001d0134
   출력 0번 = 5,000,000,000 sat

수수료 = 입력 5,000,000,000 − 출력 5,000,000,000 = 0 sat
```

`block170_lab.sh` (regtest · 값은 hex에서 나와 결정적. 이 환경에는 노드가 없어 같은 hex를 lib로 읽어 적었고, 모양은 jq 기본 출력)
```
== ① data/T-02.hex (블록 170) ==
{
  "txid": "f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
  "vin": [
    {
      "txid": "0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9",
      "vout": 0
    }
  ],
  "vout": [
    {
      "value": 10.00000000,
      "type": "pubkey"
    },
    {
      "value": 40.00000000,
      "type": "pubkey"
    }
  ]
}
== ② data/T-02_prev.hex (블록 9 코인베이스) ==
{
  "txid": "0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9",
  "vin": [
    {
      "coinbase": "04ffff001d0134"
    }
  ],
  "vout": [
    {
      "n": 0,
      "value": 50.00000000
    }
  ]
}
```
jq 1.6은 금액을 `10`, `40`, `50`처럼 줄여 찍는다(1.7부터는 Core가 준 그대로).

## 데이터
- `data/T-02.hex` — 블록 170의 두 번째 트랜잭션(첫 P2P 송금), `data/T-02_prev.hex` — 블록 9 코인베이스.
  공식 저장소에서 받을 수 없는 메인넷 원본이라 PyPI 패키지의 테스트 데이터에서 꺼냈고, SHA256d가 슬라이드의 txid와 같음을 확인했다(해시가 맞으면 바이트가 원본과 같다). 출처는 `data/SOURCES.md`.

## 퀴즈
`quiz/lesson-19.md`
