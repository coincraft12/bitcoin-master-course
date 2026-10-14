# lesson-32 · 8-1 수수료 시장: 블록 공간 경매, 추정, 보안 예산

## 목표
- 수수료가 보내는 금액이 아니라 트랜잭션 크기(vsize)에 비례하는 이유를 설명한다.
- 수수료율로 수수료를 계산하고 추정값(estimatesmartfee, 탐색기)을 해석한다.
- 반감기와 보안 예산 논의에서 수수료의 역할을 설명한다(결론은 내리지 않는다).

```
수수료(sat) = 수수료율(sat/vB) × vsize(vB)
```
- 블록 하나 = 최대 400만 WU(5-2). 채굴자는 금액이 아니라 수수료율 순으로 담는다. 수수료율 순 띠에서 약 1,000,000 vB를 잘라낸 것이 다음 블록 후보다(실제로는 패키지 단위, 8-4·8-5).
- 최소 릴레이 수수료: Core 30부터 0.1 sat/vB(이전 1 sat/vB), 증분 릴레이 수수료도 0.1. 합의가 아니라 정책(8-2).
- estimatesmartfee는 과거 통계 기반(급변에 늦게 반응), 탐색기는 현재 멤풀 기반(내 멤풀과 다를 수 있다).

## 파일
- `fee_calc.py` — 수수료 계산, gettransaction 결과 대조(`--check`). 노드 없이 실행
- `fee_lab.sh` — 실습 1~3단계와 유형별 수수료 비교 (s81-lab)

## 실습 순서 (s81-lab)
1. mempool.space에서 "다음 블록·30분·1시간" 추천 수수료율을 기록한다.
2. 메인넷 노드가 있다면 같은 시각 `estimatesmartfee 1`·`6`·`144`를 기록해 비교한다. regtest에는 수수료 시장 데이터가 없어 데이터 부족을 돌려준다 → 2-1에서 `fallbackfee`를 설정한 이유.
3. regtest: alice → bob 0.1 BTC를 `fee_rate=5`로 보내고 fee = 5 × vsize인지 확인한다. fee는 BTC 단위 음수로 나오니 sat로 바꿔 비교한다(5-2 파서로 vsize를 직접 구해도 된다).
4. 3-5(T-03)의 레거시·Taproot 코인으로 같은 금액을 보낼 때의 수수료 차이를 표로 정리한다.

## 실행
```bash
python part4/lesson-32/fee_calc.py
bash   part4/lesson-32/fee_lab.sh          # regtest 노드, miner·alice·bob 지갑, jq 필요
```

## 기대 출력
`fee_calc.py` (결정적)
```
== 8-1 퀴즈 Q1: vsize 150 vB, 20 sat/vB ==
150 × 20 = 3000 sat
== 금액과 무관: 같은 vsize면 100 BTC를 보내든 0.001 BTC를 보내든 같다 ==
보내는 금액   100 BTC, 141 vB, 5 sat/vB → 705 sat
보내는 금액 0.001 BTC, 141 vB, 5 sat/vB → 705 sat
== 최소 릴레이 수수료 (Core 30~ 기본 0.1 sat/vB, 이전 1 sat/vB) ==
141 vB × 0.1 sat/vB = 15 sat
141 vB × 1 sat/vB = 141 sat
```
소수 sat는 올림한다(141 × 0.1 = 14.1 → 15).

`fee_calc.py --check '{"fee": -0.00000705, "vsize": 141}' 5` (결정적)
```
낸 수수료 705 sat · 5 × 141 vB = 705 sat → 일치 (실효 5.00 sat/vB)
```

`fee_lab.sh` (값은 실행마다 다름)
```
# 2단계: estimatesmartfee 1·6·144
메인넷 노드 없음 → 건너뜀
regtest는 수수료 시장 데이터가 없어 데이터 부족(errors)을 돌려준다 → 2-1에서 fallbackfee를 둔 이유:
{"errors":["Insufficient data or no feerate found"],"blocks":0}   (문구는 Core 버전에 따라 다를 수 있다)
# 3단계: alice → bob 0.1 BTC, fee_rate 5 sat/vB
{
  "fee": -0.00000705,
  "vsize": 141
}
낸 수수료 705 sat · 5 × 141 vB = 705 sat → 일치 (실효 5.00 sat/vB)   (vsize는 입력 구성에 따라 다름)
# 마무리: 3-5(T-03)에서 저장한 유형별 지출로 같은 금액 송금의 수수료 차이 (5 sat/vB)
입력 유형       vsize  5 sat/vB 수수료
legacy …
p2sh-segwit …
bech32 …
bech32m …
```
네 줄의 vsize는 3-5 `measure_sizes.sh`가 출력한 값과 같다. legacy가 가장 크고 bech32m이 가장 작아야 한다. 지갑은 서명 길이를 추정해 수수료를 정하므로 드물게 1 vB 안팎이 어긋날 수 있다(3-5 결과 시트와 같은 이유).

## 퀴즈
`quiz/lesson-32.md`
