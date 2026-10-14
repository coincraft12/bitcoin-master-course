# 5강 미니 과제: 세 유형 송금 비교표 (5-4 · s5-assign)

## 과제
1. **01** regtest에서 레거시(P2PKH)·SegWit(P2WPKH)·Taproot(P2TR) 주소로 받은 코인을 각 1건 송금한다 (5-2 T-03 실습과 같은 방식).
   비교가 공정하려면 입력·출력 구성을 맞춘다: 입력 1개, 출력은 bob 0.09 BTC + 잔돈(P2WPKH 고정), 같은 수수료율.
2. **02** 각 트랜잭션 hex를 `lib/tx.py`로 파싱해 size · weight · vsize를 기록한다.
3. **03** fee ÷ vsize로 수수료율을 구하고, 같은 구성일 때 어느 유형이 가장 싼지 표로 정리한다.

**검증**: 파서 값과 `decoderawtransaction` 값이 일치해야 제출. 결과는 8-1 수수료 시장에서 다시 쓴다.

## 파일
- `exercise_compare.py` — 채울 함수 세 개(`measure`, `fee_rate_x100`, `table`). 처음엔 NotImplementedError.
- `solution/solution_compare.py` — 정답. 노드 없이 저장소 demo로, `--node`로 내 regtest 송금으로.
- `solution/send_three.sh` — 01 정답 예: 세 유형 주소로 0.1 BTC씩 받아 같은 구성으로 지출하고 `t05/spend_<유형>.hex` 저장 → 정답 스크립트로 대조·표 출력.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-22/assignment/exercise_compare.py                    # 처음엔 NotImplementedError
python part3/lesson-22/assignment/solution/solution_compare.py           # 노드 없이 (demo 세 개)
bash   part3/lesson-22/assignment/solution/send_three.sh                 # regtest: 송금 → 대조 → 표
```

## 정답 기대 출력
노드 없이 (결정적, 직접 실행한 값) — `data/demo_txs.json`: 공개 테스트 니모닉 키·가짜 UTXO로 lib이 만들고 서명한 트랜잭션.
입력 0.1 BTC 하나 → bob 0.09 BTC + 잔돈(P2WPKH), 5 sat/vB.
```
유형        size  weight  vsize  fee(sat)   sat/vB
p2pkh      219     876    219      1100     5.02
p2wpkh     223     562    141       705     5.00
p2tr       181     520    130       650     5.00
같은 수수료율이면 가장 싼 유형: p2tr (vsize 130) · 가장 비싼 p2pkh보다 89 vB 작다
```
- size(바이트)만 보면 P2WPKH 지출이 P2PKH보다 크지만, witness 할인(weight) 덕분에 vsize는 훨씬 작다 — 5-2 weight 공식의 효과.
- P2PKH의 수수료율이 5.02인 것은 수수료를 정할 때와 서명 뒤의 DER 길이가 1바이트 달라졌기 때문이다(ECDSA 서명 길이 변동, ±1 vB 정상).

`send_three.sh` (regtest, 실행마다 다름 — 모양과 크기 차이는 위와 비슷해야 한다)
```
t05/spend_legacy.hex: 파서 = decoderawtransaction True
t05/spend_bech32.hex: 파서 = decoderawtransaction True
t05/spend_bech32m.hex: 파서 = decoderawtransaction True
유형        size  weight  vsize  fee(sat)   sat/vB
legacy     220     880    220      1100     5.00 (실행마다 다름)
bech32     222     561    141       705     5.00 (실행마다 다름)
bech32m    181     520    130       650     5.00 (실행마다 다름)
같은 수수료율이면 가장 싼 유형: bech32m (vsize 130) · 가장 비싼 legacy보다 90 vB 작다
```
`True`가 아니면 제출하지 않는다. 다르면 5-2 체크(바이트 뒤집기, stripped 조립, 올림)를 먼저 의심한다.

## 제출물
비교표(유형 · size · weight · vsize · fee · sat/vB)와 "어느 유형이 왜 가장 싼가" 두세 줄. 3-5(lesson-13) 측정표와 비교해도 좋다.
