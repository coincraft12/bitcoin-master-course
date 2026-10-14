# lesson-09 · 3-1 공개키 암호와 secp256k1

## 목표
- 개인키·공개키 관계를 스칼라 곱 `Q = d·G` 하나로 설명한다.
- 점 덧셈·스칼라 곱을 구현하고(`lib/ec.py`) 검증용 라이브러리와 대조한다.
- 안전한 개인키 생성(`secrets`)과 약한 난수의 위험을 설명한다.

## 만드는 코드
- `lib/ec.py` — `FIELD_P`, `N`, `G`, `is_on_curve(P)`, `point_add(P, Q)`, `point_mul(P, k)` (점이 먼저, 스칼라가 나중)
- `lib/keys.py` — `new_private_key()`, `public_key(d)`

> 교육용 구현: 상수 시간 연산이 아니므로 실제 자금의 키에 쓰지 말 것. `pow(x, -1, p)`는 Python 3.8+.

## 실습 순서
1. `lib/ec.py`의 상수와 `is_on_curve` (s31-code1) → `point_add` (s31-code2) → `point_mul`과 `lib/keys.py` (s31-code3)
2. 확인 스크립트: 네 줄이 모두 True인지
3. 같은 개인키를 coincurve로 계산해 x, y 대조 (선택: `pip install coincurve`)
4. 보충: 약한 난수로 만든 키가 재현되는 시연

## 실행 (저장소 최상위에서)
```bash
python part2/lesson-09/ec_check.py
python part2/lesson-09/compare_coincurve.py        # 새 키로 대조
python part2/lesson-09/compare_coincurve.py 1      # 개인키 1로 대조
python part2/lesson-09/weak_rng.py
```

## 기대 출력
`ec_check.py` — 앞 네 줄은 항상 같다. 키는 실행마다 다르다.
```
is_on_curve(G)               : True
point_mul(G, N) is None      : True
point_mul(G, 2) == G + G     : True
public_key(1) == G           : True
개인키 d : 0xe4d002cc400fcbc93baba1b478b6cc14fc9b0d5ce0e2fff7d6fe7790229c6070 (실행마다 다름)
공개키 Q : 0x2f6f645e55c472ac1332eaf6e1e8550b4f5c442f5232f1f01cad8eec6ba599c8 0xebecbe7b70eb1909a604aaabef83ef7d5696dfb9fa6c157f932fa869be823e02 (실행마다 다름)
Q가 곡선 위에 있는가: True
```
하나라도 False면 상수를 잘못 붙였을 가능성이 가장 크다.

`compare_coincurve.py 1` (결정적)
```
d          : 0x1
lib x      : 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
coincurve x: 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
lib y      : 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
coincurve y: 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
일치       : True
```
coincurve가 없으면 `coincurve가 없습니다. 대조하려면: pip install coincurve`만 출력한다.

`weak_rng.py`
```
피해자 공개키 x: 0x2c99923e751900e8b2a66341bc79003b6bf2655a318a843ac7673219bd8c3002 (실행마다 다름)
찾음: 시드 1791973281, 시도 387번, 3.5초 (실행마다 다름)
키 공간은 2^256이어도 실제 후보는 수천 개뿐이었다.
```

## 퀴즈
`quiz/lesson-09.md`
