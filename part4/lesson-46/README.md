# lesson-46 · 11-3 채굴 풀과 Stratum V2

## 목표
- 채굴 풀이 생겨난 이유와 셰어의 역할을 설명한다.
- PPS, FPPS, PPLNS 보상 방식을 비교한다.
- 해시파워 분산과 템플릿 결정권 집중을 구분하고 Stratum V2의 목표를 설명한다.

| 방식 | 채굴자 수입 | 위험을 지는 쪽 |
|---|---|---|
| PPS (셰어당 고정 지급) | 셰어마다 기대값만큼 즉시, 보조금 기준 | 풀 운영자 |
| FPPS | PPS + 수수료 기대값까지 | 풀 운영자 |
| PPLNS (최근 N개 셰어) | 블록을 찾았을 때 최근 셰어 비율로 분배 | 채굴자 (변동성) |

Stratum V2: Job Declaration(채굴자가 자기 노드에서 고른 트랜잭션으로 템플릿 제안), 통신 암호화. 2026년 6월 DMND·GoMining이 Job Declaration으로 채굴한 블록(955,318) 보도, 상위 대형 풀의 도입은 아직 불분명.

## 파일
- `coinbase_tags.py` — s113-lab 코드 (메인넷 최근 1,000블록 코인베이스 태그 집계)
- `tag_offline.py` — 슬라이드 방식 태그 추출과 태그 사전(data/coinbase_tags.json)으로 풀 찾기 (노드 없이)
- `data/coinbase_tags.json` — bitcoin-data/mining-pools의 `pools.json` 원본(태그 → 풀, 지급 주소 → 풀). 출처는 `data/SOURCES.md`

## 실습 순서 (s113-lab)
1. 메인넷 노드가 있으면 `coinbase_tags.py`로 최근 1,000블록 → 상위 10개 태그와 비율(1,000블록이라 개수 ÷ 10 = %).
2. 메인넷 노드가 없으면 공개 탐색기의 풀 통계 페이지와 `tag_offline.py`로 진행한다. 탐색기에서 코인베이스 hex를 복사해 `tag_offline.py <hex>`로 넣어 볼 수 있다.
3. 한 풀이 여러 이름으로 잡히거나 태그 없는 블록이 생긴다 → 탐색기 통계와 차이를 토론한다. 실제 분석 서비스는 보상 지급 주소 패턴도 쓴다(태그 사전의 `payout_addresses`, 온체인 데이터 분석가 트랙).

## 실행
```bash
python part4/lesson-46/tag_offline.py
python part4/lesson-46/coinbase_tags.py            # 메인넷 노드 필요 (수 분 걸린다)
python part4/lesson-46/coinbase_tags.py regtest    # 형식만 확인
```
슬라이드 코드에는 `import re`, `from collections import Counter`, `from lib.rpc import RPC` 줄이 화면에서 빠져 있어 스크립트에 넣었다. 1,000블록이 안 되는 체인(regtest)에서도 돌도록 시작 높이를 1 이상으로 잘랐다.

## 기대 출력
`tag_offline.py` (결정적, 태그 사전은 받은 날짜 기준)
```
== 1. 제네시스 코인베이스 (scriptSig) ==
  출력 가능 문자: ·······EThe Times 03/Jan/2009 Chancellor on brink of second bailout for banks
  슬라이드 방식 태그: EThe · 태그 사전 풀: (사전에 없음)
== 2. 태그 사전 ==
  태그 174개 · 풀 132곳 · 보상 지급 주소 201개
  태그가 2개 이상인 풀: 30곳
  BTCC             태그 4개 예: ['/BTCC/', 'BTCChina Pool', 'BTCChina.com']
  Binance Pool     태그 4개 예: ['/Binance/', 'binance', 'binance.com/']
  EMCDPool         태그 4개 예: ['/EMCD/', '/one_more_mcd/', 'emcd.io']
  BTC.com          태그 3개 예: ['/BTC.COM/', '/BTC.com/', 'btccom']
  Bixin            태그 3개 예: ['/Bixin/', '/HaoBTC/', 'HAOBTC']
```
제네시스의 "EThe"는 push 길이 바이트 0x45('E')가 글자로 붙어 나온 것이다. 슬라이드 방식이 단순화라서 생기는 오차의 예다.

`coinbase_tags.py` (메인넷): 한 줄에 태그(24칸), 블록 수, 비율(%)이 상위 10개까지 나온다. 태그 문자열·순위·비율은 집계 시점마다 다르므로 같은 시각의 탐색기 풀 통계와 나란히 적어 비교한다. `regtest`로 돌리면 regtest 코인베이스에는 4글자 이상 단어가 없어 `(unknown)` 한 줄만 나온다.

## 퀴즈
`quiz/lesson-46.md`
