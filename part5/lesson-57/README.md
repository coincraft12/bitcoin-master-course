# lesson-57 · 14-1 블록 공간 논쟁과 BIP-110

## 목표
- 인스크립션과 Runes가 블록 공간에 데이터를 기록하는 구조를 설명한다 (s141-methods).
- OP_RETURN 정책 변경을 둘러싼 Core·Knots 논쟁을 양측 논리로 정리한다 (s141-v30, s141-sides).
- 정책 논쟁이 합의 변경 제안(BIP-110)으로 번진 경과와 결과를 설명한다 (s141-timeline, s141-lesson).

| 방법 | 위치 | 특징 |
|---|---|---|
| OP_RETURN 출력 | 쓸 수 없는 출력 | UTXO 집합을 오염시키지 않음, 오래전부터 표준 정책으로 크기 제한 |
| 인스크립션 | Taproot 스크립트 경로 witness의 `OP_FALSE OP_IF … OP_ENDIF` 봉투 | witness 할인(5-2)으로 대용량 기록, 2023년부터 급증 |
| Runes | OP_RETURN 출력 | 대체 가능 토큰 규약, 2024년 4월 반감기 블록에 출시 |
| 가짜 공개키·가짜 출력 | 일반 출력 자리 | 쓸 수 없는 UTXO가 영구히 남아 노드 부담 증가 |

Bitcoin Core v30 (2025년 10월) 정책 변경: 이전 OP_RETURN 출력 트랜잭션당 1개, 데이터 약 80바이트(스크립트 83바이트) → v30 `-datacarriersize` 기본 100,000(사실상 최대 트랜잭션 크기가 먼저 한도), 여러 개 허용(합산 적용), `-datacarriersize=83`으로 이전 한도 복원 가능. **합의 규칙은 그대로** — 바뀐 것은 내 노드가 무엇을 중계하느냐(8-2의 이중 필터). 같은 릴리스: 레거시(BDB) 지갑 제거, 최소 릴레이 수수료 0.1 sat/vB, 표준 트랜잭션의 레거시 서명 연산 2,500개 한도(BIP54 대비).

경과(s141-timeline): 2025년 4~5월 한도 제거 제안과 논쟁 → 9월 Knots 노드 급증(공개 노드 비중 집계 방식에 따라 12~25%) → 10월 v30 출시 → 10월 말 1년 임시 소프트포크 제안(BIP-444 → BIP-110 "Reduced Data Temporary Softfork") → 2026년 5월 Knots 표준 빌드에 BIP-110 강제 옵션 → 2026년 8월 9일 블록 961,632에서 BIP-110 강제 노드 분리. 직전 2주 채굴자 신호 2.53%(기준 55%), 분리 체인은 블록 2개 후 사실상 정지, 본 체인은 영향 없이 계속. 같은 시기 드라이브체인 진영의 eCash 하드포크 계획은 BIP-110과 다른 사안이다.

## 파일
- `data_tx.sh` — s141-lab 슬라이드 명령 그대로(인자 없이) + 데이터 크기를 바꿔 가며(`-stdin` 사용)
- `opreturn_policy.py` — 노드 없이: 데이터 N바이트 → nulldata 스크립트 크기 → 기본 설정/`-datacarriersize=83`에서 중계 여부

## 실습 (s141-lab)
```bash
DATA=$(python3 -c "print(b'CoinCraft Bitcoin Master Course'.hex())")
RAW=$(bitcoin-cli -regtest createrawtransaction '[]' "[{\"data\":\"$DATA\"}]")
FUNDED=$(bitcoin-cli -regtest -rpcwallet=alice fundrawtransaction $RAW | jq -r .hex)
SIGNED=$(bitcoin-cli -regtest -rpcwallet=alice signrawtransactionwithwallet $FUNDED | jq -r .hex)
bitcoin-cli -regtest testmempoolaccept "[\"$SIGNED\"]"
bitcoin-cli -regtest decoderawtransaction $SIGNED | jq '.vout[] | select(.scriptPubKey.type=="nulldata")'
```
스크립트로 (저장소 최상위에서):
```bash
bash part5/lesson-57/data_tx.sh            # 위 명령 그대로 (31바이트)
bash part5/lesson-57/data_tx.sh 80
bash part5/lesson-57/data_tx.sh 81
bash part5/lesson-57/data_tx.sh 99000
```
`-datacarriersize=83`으로 다시 띄워 같은 크기를 비교한다:
```bash
bitcoin-cli -regtest stop
bitcoind -regtest -daemon -datacarriersize=83
bitcoin-cli -regtest loadwallet alice
bash part5/lesson-57/data_tx.sh 80; bash part5/lesson-57/data_tx.sh 81
# 끝나면 옵션 없이 다시 띄운다
```
메인넷 노드·탐색기 과제: 인스크립션 트랜잭션 witness에서 봉투(`OP_FALSE OP_IF … OP_ENDIF`)와 콘텐츠 유형 표시 찾기, Runes 트랜잭션의 OP_RETURN 페이로드 길이 확인.

## 기대 출력
슬라이드 표 (Core 31.1로 직접 확인한 결과 — 슬라이드 수치)
| 데이터 크기 | 기본 설정 (Core 31.1) | `-datacarriersize=83` |
|---|---|---|
| 31바이트 | 허용 | 허용 |
| 80바이트 | 허용 | 허용 |
| 81바이트 | 허용 | 거부 · datacarrier |
| 99,000바이트 | 허용 (vsize 99,141) | 거부 · datacarrier |

`data_tx.sh` (인자 없이). nulldata 출력은 결정적이다 — 스크립트·디스크립터 체크섬은 Core 디스크립터 체크섬 알고리즘(Bitcoin Core `test/functional/test_framework/descriptors.py`)으로 직접 계산해 확인했다. `n`(출력 위치)과 txid, vsize는 실행마다 다름.
```
[
  {
    "txid": "…(실행마다 다름)",
    "wtxid": "…",
    "allowed": true,
    "vsize": 152,      (alice 입력이 P2WPKH 1개일 때 계산값 · 입력 구성에 따라 다름)
    "fees": { … }
  }
]
{
  "value": 0.00000000,
  "n": 0,      (0 또는 1, 실행마다 다름)
  "scriptPubKey": {
    "asm": "OP_RETURN 436f696e437261667420426974636f696e204d617374657220436f75727365",
    "desc": "raw(6a1f436f696e437261667420426974636f696e204d617374657220436f75727365)#9l2dfsje",
    "hex": "6a1f436f696e437261667420426974636f696e204d617374657220436f75727365",
    "type": "nulldata"
  }
}
```
`6a` = OP_RETURN, `1f` = 31바이트 푸시.

`data_tx.sh 81` 를 `-datacarriersize=83` 노드에서 (형태)
```
{"allowed":false,"vsize":null,"reject-reason":"datacarrier"}
{"vsize":…,"nulldata":[{"n":0,"script_bytes":84}]}
```

`opreturn_policy.py` (결정적, 직접 실행해 확인)
```
       데이터       스크립트   기본 설정 (100,000)      -datacarriersize=83
      31B       33B   허용                   허용
      80B       83B   허용                   허용
      81B       84B   허용                   거부 · datacarrier
  99,000B   99,006B   허용                   거부 · datacarrier
40바이트 OP_RETURN 2개: 스크립트 합 84B → 기본 허용, 83 설정 거부 (합산 적용)
```
- 80바이트까지 `OP_PUSHDATA1`(1+1+1+80 = 83), 99,000바이트는 65,535를 넘어 `OP_PUSHDATA4`(1+1+4+99,000 = 99,006).
- 같은 합의 규칙, 다른 정책: 기본 노드가 중계한 81바이트 트랜잭션이 블록에 들어가면 83 설정 노드도 유효하다고 인정한다.

## 흔히 막히는 지점
- 큰 데이터를 명령줄에 넣다가 `Argument list too long` — 인자 하나가 약 128KB를 넘으면 실패한다. `bitcoin-cli -stdin`으로 넣는다(`data_tx.sh N`이 그렇게 한다).
- `-datacarriersize`를 바꾸려면 노드를 다시 띄워야 한다. 끝나면 기본값으로 돌려놓는다.
- 기본 설정에서 81바이트가 허용되는 것이 정상이다(v30 이후). 이전 버전 노드라면 거부된다.

## 퀴즈
`quiz/lesson-57.md`
