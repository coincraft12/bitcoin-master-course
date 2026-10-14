# lesson-21 · 5-3 잔돈과 코인 선택: 잔돈 누락, 더스트, 코인 선택 알고리즘

## 목표
- 잔돈 출력이 필요한 이유와, 빠뜨리면 차액 전부가 수수료가 된다는 점을 설명한다.
- `createrawtransaction`으로 잔돈을 포함한 송금을 직접 구성·서명·전파한다.
- 코인 선택(Branch and Bound · Knapsack · Single Random Draw · CoinGrinder, waste 지표)이 수수료와 프라이버시에 주는 영향을 설명한다.

## 코드
- `change_lab.sh` — LAB ①②③ (s53-lab1~3) 한 번에. 5-2(lesson-20)의 `t03_segwit.sh`로 alice가 받은 0.3 BTC 코인을 쓴다.
- `fee_check.py` — 수수료 = 입력 합 − 출력 합, 수수료율 = 수수료 ÷ vsize를 5-2 파서로 계산. 더스트 기준(P2PKH 546 · P2WPKH 294 · P2TR 330 sat 미만)도 표시.

## 실습 순서
1. **준비** miner로 블록 1개 → alice `listunspent`에서 0.3 BTC 코인의 TXID·VOUT, bob 받는 주소, alice 잔돈 주소(`getrawchangeaddress bech32`).
2. **LAB ① 일부러 실수** bob 0.1 BTC 출력 하나만 적고 서명해 `sendrawtransaction` → 0.2 BTC가 수수료로 잡혀 maxfeerate(기본 0.10 BTC/kvB) 초과로 거부. `testmempoolaccept`로 거부 사유 재확인.
3. **LAB ② 잔돈 포함** bob 0.1 + 잔돈 0.1999 → 수수료 0.0001 BTC = 10,000 sat. 전파 전에 `decoderawtransaction | jq '{vsize, vout: [.vout[].value]}'`로 금액을 눈으로 확인하는 습관. 5-2 파서로 같은 vsize가 나오는지 `fee_check.py`로 확인.
4. **LAB ③ Core에 맡기기** 입력을 비운 `createrawtransaction` + `fundrawtransaction … '{"fee_rate":10}'` → `fee`와 `changepos`. 여러 번 실행하면 잔돈 위치가 무작위로 바뀐다(분석가의 잔돈 식별 방해).

## 실행 (저장소 최상위에서)
```bash
bash   part3/lesson-21/change_lab.sh         # regtest 노드, miner·alice·bob 지갑, lesson-20의 0.3 BTC 코인
python part3/lesson-21/fee_check.py           # 노드 없이 (저장소 demo 트랜잭션)
python part3/lesson-21/fee_check.py change_tx.hex 30000000
```

## 기대 출력
`change_lab.sh` — txid·주소·vsize는 실행마다 다름
```
{"txid":"7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95","vout":1,"amount":0.3} (실행마다 다름)
TXID=7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95 VOUT=1 (실행마다 다름)
== 1단계: 출력 하나뿐 (0.2 BTC가 수수료로) ==
error code: -25
error message:
Fee exceeds maximum configured by user (e.g. -maxtxfee, maxfeerate)
→ 기대한 거부: 수수료가 maxfeerate(기본 0.10 BTC/kvB)를 넘음
{"allowed":false,"reject-reason":"max-fee-exceeded"}
== 2단계: 잔돈을 넣은 송금 ==
{"vsize":141,"vout":[0.1,0.1999]} (vsize는 실행마다 다름)
e2bb6396a96d625555316dabb10b0fbaea0a485077f62c9f6b8842ada63aafa8 (실행마다 다름)
== change_tx.hex ==
  출력 0:  10,000,000 sat (P2WPKH)
  출력 1:  19,990,000 sat (P2WPKH)
  수수료 = 30,000,000 − 29,990,000 = 10,000 sat · vsize 141 vB → 70.92 sat/vB (실행마다 다름)
== 3단계: Core에 맡기기 (두 번 실행해 changepos 비교) ==
{"fee":0.0000141,"changepos":0} (실행마다 다름)
{"fee":0.0000141,"changepos":1} (실행마다 다름)
```
- 1단계의 오류 문구는 Core 버전에 따라 조금 다를 수 있다. 핵심은 "최대 수수료 초과로 거부"와 `allowed: false`.
- 2단계 수수료는 언제나 10,000 sat. 수수료율은 그 트랜잭션의 vsize에 따라 다르다(위 예는 vsize 141).

`fee_check.py` (결정적, 직접 실행한 값)
```
== demo p2pkh 입력 지출 ==
  출력 0:   9,000,000 sat (P2WPKH)
  출력 1:     998,900 sat (P2WPKH)
  수수료 = 10,000,000 − 9,998,900 = 1,100 sat · vsize 219 vB → 5.02 sat/vB
== demo p2wpkh 입력 지출 ==
  출력 0:   9,000,000 sat (P2WPKH)
  출력 1:     999,295 sat (P2WPKH)
  수수료 = 10,000,000 − 9,999,295 = 705 sat · vsize 141 vB → 5.00 sat/vB
== demo p2tr 입력 지출 ==
  출력 0:   9,000,000 sat (P2WPKH)
  출력 1:     999,350 sat (P2WPKH)
  수수료 = 10,000,000 − 9,999,350 = 650 sat · vsize 130 vB → 5.00 sat/vB
== 0.3 BTC 입력, 출력은 bob 0.1 BTC 하나 (잔돈 누락) ==
  출력 0:  10,000,000 sat (P2WPKH)
  수수료 = 30,000,000 − 10,000,000 = 20,000,000 sat · vsize 110 vB → 181818.18 sat/vB
  경고: 수수료율이 sendrawtransaction 기본 maxfeerate 0.10 BTC/kvB를 넘는다 → 전파 거부
```
마지막 예가 s53-q의 상황이다. 합의 규칙상으로는 유효한 트랜잭션이고, 막아 주는 것은 노드·지갑의 정책이다(s53-myth).

## 퀴즈
`quiz/lesson-21.md`
