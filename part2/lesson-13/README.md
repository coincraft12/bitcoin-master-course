# lesson-13 · 3-5 Taproot 주소: bech32m, P2TR, 유형별 크기 비교

## 목표
- bech32m(BIP350)이 도입된 이유(마지막 글자 p 앞 q 삽입·삭제를 놓치는 약점)를 설명한다.
- P2TR 주소 = bech32m(v1, 출력키 32B), 잠금 스크립트 `0x51 0x20 ‖ 출력키`를 설명하고 Core에서 생성한다.
- 유형별 지출 크기를 실제 송금으로 재고 알맞은 유형을 고른다 (T-03).

## 코드
- `lib/keys.py` — `p2tr_address(output_xonly, hrp="bc")`: 이미 조정된 32바이트 출력키를 bech32m으로 적는다.
  내부키 → 출력키 조정은 6-4에서 `lib/taproot.py`의 `output_key`로 직접 계산한다.
- `bech32m_rules.py` — 버전별 인코딩 규칙, BIP350 무효 벡터, bech32 약점 재현
- `measure_sizes.sh` — 실습 T-03 (s35-lab, s35-result)

| 유형 | mainnet 접두어 | 출력 | 입력(단일 서명) |
|---|---|---|---|
| P2PKH | 1 | 34 vB | 약 148 vB |
| P2SH-P2WPKH | 3 | 32 vB | 약 91 vB |
| P2WPKH | bc1q (42자) | 31 vB | 약 68 vB |
| P2WSH | bc1q (62자) | 43 vB | 스크립트에 따라 |
| P2TR | bc1p (62자) | 43 vB | 약 57.5 vB |

## 실행
```bash
python part2/lesson-13/bech32m_rules.py
bash   part2/lesson-13/measure_sizes.sh        # regtest 노드, alice·bob·miner 지갑 필요
```

## 기대 출력
`bech32m_rules.py` (결정적)
```
v0 + 32B (bech32) : bc1qqqqsyqcyq5rqwzqfpg9scrgwpugpzysnzs23v9ccrydpk8qarc0szrtjt7
v1 + 32B (bech32m): bc1pqqqsyqcyq5rqwzqfpg9scrgwpugpzysnzs23v9ccrydpk8qarc0sg5tmnz
v1을 bech32로 적으면: bc1pqqqsyqcyq5rqwzqfpg9scrgwpugpzysnzs23v9ccrydpk8qarc0sagmhkq → decode (None, None)
무효 벡터: bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqh2y7hd → (None, None)
무효 벡터: tb1z0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqglt7rf → (None, None)
무효 벡터: BC1S0XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ54WELL → (None, None)
무효 벡터: bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kemeawh → (None, None)
무효 벡터: tb1q0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq24jc47 → (None, None)

마지막 글자가 p인 bech32  : bc1qjlhuryrczhcnu6sz6s2f5z0f55uf8z8d75xn8p
p 앞에 q 삽입             : bc1qjlhuryrczhcnu6sz6s2f5z0f55uf8z8d75xn8qp
체크섬만 보면              : Encoding.BECH32
segwit 규칙(v0 길이)으로는 : (None, None)
bech32m에 같은 삽입        : None
```
q를 끼워 넣은 문자열도 bech32 체크섬은 통과한다. v0은 프로그램 길이(20/32B) 검사로 걸러지지만 길이가 자유로운 미래 버전에는 위험해서 bech32m이 나왔다.

`measure_sizes.sh` — 주소·vsize는 실행마다 조금 다르다. legacy가 가장 크고 bech32m이 가장 작아야 하며, 차이는 위 표의 입력 크기 차이와 대략 맞아야 한다(ECDSA 서명 길이 변동으로 ±1 vB는 정상).
```
legacy mwvo16E33unXjzAaxd6bC6WTKxFzHGf8V7 (실행마다 다름)
p2sh-segwit 2MxvXjkMqNdpYYu1cdA2Qvo1duA7AgCyjTW (실행마다 다름)
bech32 bcrt1qnhjc82vswn572e55yu296atlzn6lqfg9c5ml0j (실행마다 다름)
bech32m bcrt1pg3tsnht8kypl089w5ez0xy23tf9ke99wypewteeyj44k3kuv8vcqm83a40 (실행마다 다름)

입력 유형     vsize(vB)   weight 5 sat/vB 수수료(sat)
legacy              220      880               1100 (실행마다 다름)
p2sh-segwit         164      654                820 (실행마다 다름)
bech32              141      562                705 (실행마다 다름)
bech32m             130      520                650 (실행마다 다름)

저장: data/T-03/spend_{legacy,p2sh-segwit,bech32,bech32m}.hex
```
수수료 열은 vsize × 5 sat. 위 vsize·weight 예시는 측정값이 아니라, 입력 1개(ECDSA 서명 72바이트 가정) + P2WPKH 출력 2개(받는 쪽, 잔돈)로 계산한 근삿값이다. 측정값으로 직접 표를 채운다(s35-result).

## 퀴즈
`quiz/lesson-13.md`
