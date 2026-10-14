# lesson-34 · 8-3 RBF: 대체 규칙, full RBF, 0-확인 위험

## 목표
- RBF(Replace-By-Fee)의 원리와 대체 조건을 설명한다.
- `bumpfee`로 수수료를 올리고 송금을 사실상 취소한다.
- 0-확인 결제를 신뢰하면 안 되는 이유를 설명한다.

원리는 합법적인 이중지불이다. 같은 입력 + 같은 출력 + 더 높은 수수료 = 수수료 인상, 같은 입력 + 출력을 내 주소로 + 더 높은 수수료 = 사실상 취소.

| 대체 규칙 (s83-rules) | 이유 |
|---|---|
| 대체본 절대 수수료 > 원본(과 함께 축출되는 것들)의 합 | 채굴자 이익 보장 |
| 늘어난 수수료 ≥ 대체본 크기 × 증분 릴레이 수수료 | 재전파 대역폭 비용 지불 |
| 한 번에 축출되는 트랜잭션 수 상한 | 연쇄 축출 DoS 방지 |
| Core 31~ 교체 후 멤풀 피레이트 다이어그램이 엄격히 더 좋아야 함 | 실제 채굴 이익과 일치 (8-5) |

opt-in(BIP125, nSequence < 0xfffffffe) → Core 28 `mempoolfullrbf` 기본값 1 → Core 29 옵션 제거, full RBF가 표준 동작. 표시 여부는 더 이상 보호 수단이 아니다.

## 파일
- `rbf_rules.py` — 대체 규칙 1·2를 s83-idea 숫자로 확인 (노드 없이 실행)
- `rbf_lab.sh` — 실습 ①~④ (s83-lab1, s83-lab2)

## 실습 순서
1. alice → bob 0.1 BTC를 `fee_rate=1`로 보내 TX1, `getmempoolentry`로 vsize·fees 확인. bob 지갑에는 대기 중(untrusted_pending)으로 보인다.
2. `bumpfee $TX1 options='{"fee_rate":10}'` → TX2. TX1을 조회하면 "멤풀에 없음" 오류가 정상이다. TX2는 vsize가 거의 같고 fees가 크게 늘었다. 두 트랜잭션을 나란히 놓으면 입력은 같고 txid가 바뀌었으며 잔돈 출력이 줄었다.
3. alice의 새 주소 ME로 `outputs` 옵션을 주어 `fee_rate=20`으로 대체 → 출력이 alice 자신에게 간다(옵션 문자열의 따옴표 이스케이프에 주의).
4. 블록 1개 → bob의 `getbalances`에 0.1 BTC가 없다. 상점이었다면 대금을 잃었다.

## 실행
```bash
python part4/lesson-34/rbf_rules.py
bash   part4/lesson-34/rbf_lab.sh        # regtest 노드, miner·alice·bob 지갑, jq 필요
```

## 기대 출력
`rbf_rules.py` (결정적)
```
원본 A 수수료    100000 sat
대체본 B 수수료  150000 sat (잔돈이 50000 sat 줄어든 만큼)
규칙 1 (B > A): True · 규칙 2 (증가분 ≥ 141 vB × 0.1 sat/vB): True
== 1 sat씩 올려 다시 보내기가 막히는 이유 ==
대체본 수수료 100001 sat → 규칙1 True, 규칙2 False (최소 100015 sat)
대체본 수수료 100014 sat → 규칙1 True, 규칙2 False (최소 100015 sat)
대체본 수수료 100015 sat → 규칙1 True, 규칙2 True (최소 100015 sat)
== 피닝(8-5): 원본에 거대한 저수수료 자식이 붙어 함께 축출돼야 한다면 ==
원본+자식 190000 sat보다 커야 함 → B(150000 sat)는 규칙1 False, 최소 190015 sat 필요
```
141 vB는 입력 1·출력 2 P2WPKH 트랜잭션의 크기(8-4 s84-lab2 값), 9만 vB 자식은 설명용 예다. 증분 릴레이 수수료 0.1 sat/vB는 Core 30~ 기본값(s81-estimate).

`rbf_lab.sh` (txid·잔액은 실행마다 다름, vsize는 입력 구성에 따라 다름)
```
TX1=0c5e…41f7                                          (실행마다 다름)
{
  "vsize": 141,
  "fees": { "base": 0.00000141, "modified": 0.00000141, "ancestor": 0.00000141, "descendant": 0.00000141, … }
}
# bob 지갑에는 '대기 중'으로 보인다
{"trusted":5.00000000,"untrusted_pending":0.10000000,"immature":0.00000000}
TX2=a913…5b02                                          (실행마다 다름)
error code: -5
error message:
Transaction not in mempool
{
  "vsize": 141,
  "fees": { "base": 0.00001410, … }
}
# TX1과 TX2 비교: 입력은 같고, txid가 바뀌고, 잔돈 출력이 줄었다
{"txid":"0c5e…41f7","vin":["7d1a…:0"],"vout":[{"value":0.1,…},{"value":4.89999859,…}]}
{"txid":"a913…5b02","vin":["7d1a…:0"],"vout":[{"value":0.1,…},{"value":4.8999859,…}]}
{ "txid": "e27b…c8a0", "origfee": 0.00001410, "fee": 0.00002820, "errors": [] }   (fee는 대체본 크기에 따라 다름)
…
{
  "mine": { "trusted": 5.00000000, "untrusted_pending": 0.00000000, "immature": 0.00000000 }
}
→ bob은 한때 '대기 중 0.1 BTC'를 보았지만 결국 받지 못했다 (0-확인 결제 위험의 재현)
```
`getmempoolentry`의 fees 아래 항목 구성은 Core 버전에 따라 다르다(Core 31은 chunk 값이 더해진다, 8-4). 핵심은 TX1이 멤풀에서 사라지고 TX2가 들어왔다는 것, bob의 untrusted_pending 0.1이 마지막에 0이 된다는 것이다.

## 실무 팁
대체본은 txid가 바뀐다. 상대에게 txid를 알려 줬다면 새 txid를 다시 알린다. 소액·저위험이 아니면 최소 1 확인을 기다리거나 라이트닝(13강)을 쓴다.

## 퀴즈
`quiz/lesson-34.md`
