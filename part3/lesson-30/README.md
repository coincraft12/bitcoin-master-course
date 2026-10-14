# lesson-30 · 7-3 Schnorr 서명: BIP340 설계, 구현, 테스트 벡터

## 목표
- BIP340 서명(x-only·짝수 y, 태그드 해시 aux/nonce/challenge, 챌린지에 공개키 포함)의 생성·검증 절차를 설명하고 구현한다.
- 공식 테스트 벡터 19개로 구현을 검증한다.
- 고정 크기(64B), 선형성(키·서명 집계 → MuSig2), 일괄 검증의 실익을 설명한다.

## 코드
- `lib/schnorr.py` — 이 차시에 작성. s73-code1·2 그대로: `b32`, `to_int`, `even_y`, `xor`, `sign(msg, seckey, aux_rand) -> 64B`, `verify(msg, pubkey, sig) -> bool`.
  덧붙인 것: `pubkey_gen(seckey) -> x-only 32B`.
- `lib/taproot.py`의 `lift_x`에 **x ≥ FIELD_P면 실패** 한 줄을 이 차시에 추가한다(벡터 14번이 이 경우).
- `run_vectors.py` — s73-code2 벡터 루프
- `linearity.py` — s73-linear: s₁ + s₂가 P₁ + P₂에 대한 서명 하나로 검증되는 것 확인 (단순 합산은 rogue key 공격에 취약 → MuSig2)

## 실습 순서
1. 절차 장(s73-procs)과 `sign` 코드를 한 줄씩 짝지어 작성한다.
2. `verify`: 길이 검사 → lift_x 실패면 False → r ≥ p 또는 s ≥ n이면 False → R = sG − eP (빼기는 P에 n − e를 곱해 더하기) → 무한원점·홀수 y·x 불일치면 False.
3. 벡터 19개 실행. FAIL이 나면 그 행의 comment(무한원점, 홀수 R, 범위 초과)를 읽고 빠진 검사를 찾는다 — 그것 자체가 학습 활동.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-30/run_vectors.py
python part3/lesson-30/linearity.py
```

## 기대 출력 (결정적, 직접 실행한 값)
`run_vectors.py`
```
 0 PASS TRUE  
 1 PASS TRUE  
 2 PASS TRUE  
 3 PASS TRUE  test fails if msg is reduced modulo p or n
 4 PASS TRUE  
 5 PASS FALSE public key not on the curve
 6 PASS FALSE has_even_y(R) is false
 7 PASS FALSE negated message
 8 PASS FALSE negated s value
 9 PASS FALSE sG - eP is infinite. Test fails in single verification if has_even_y(inf) is defined as true and x(inf) as 0
10 PASS FALSE sG - eP is infinite. Test fails in single verification if has_even_y(inf) is defined as true and x(inf) as 1
11 PASS FALSE sig[0:32] is not an X coordinate on the curve
12 PASS FALSE sig[0:32] is equal to field size
13 PASS FALSE sig[32:64] is equal to curve order
14 PASS FALSE public key is not a valid X coordinate because it exceeds the field size
15 PASS TRUE  message of size 0 (added 2022-12)
16 PASS TRUE  message of size 1 (added 2022-12)
17 PASS TRUE  message of size 17 (added 2022-12)
18 PASS TRUE  message of size 100 (added 2022-12)
19/19 PASS
```
`linearity.py`
```
합친 공개키 P₁+P₂: 15db312206fd379794c95653090fc1af25f437ae41d5281cec57db1ea4eae0d8
s₁ + s₂로 만든 64B 서명: efeaabf6db55b58b39667a4e995cdf0b5dcc46e0c2dc219484a41d9f5379a2d4456773d9256738b154d4ec374a3653bd94d2bd0fbed878b7a33c280a4ec08d71
P₁+P₂에 대한 보통의 BIP340 검증: True
```

## 테스트
`python -m pytest tests/test_schnorr.py` — 벡터 19개 전부 서명·검증, 변조 실패.

## 퀴즈
`quiz/lesson-30.md`
