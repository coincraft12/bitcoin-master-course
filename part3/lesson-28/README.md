# lesson-28 · 7-1 ECDSA: 서명·검증, low-S, DER, 구현

## 목표
- ECDSA 서명(k → R → r, s = k⁻¹(z + r·d))과 검증(w, u₁, u₂, X = u₁G + u₂Q)을 단계별로 설명한다.
- 서명·검증 함수를 직접 구현하고 검증된 라이브러리와 상호 검증한다.
- DER 인코딩(0x30 · 0x02 · 최소 바이트 · 최상위 비트 0x00)과 low-S 규칙이 존재하는 이유(5-2 가변성)를 설명한다.

## 코드
- `lib/ecdsa.py` — 이 차시에 작성. s71-code1·2 그대로: `sign(d, z, k=None) -> (r, s)`(low-S), `verify(Q, z, r, s) -> bool`, `der(r, s) -> bytes`.
  덧붙인 것: `parse_der(sig)`(실제 트랜잭션 서명 검증용), 7-2에서 추가하는 `rfc6979_nonce(d, z)`, `sign_rfc6979(d, z)`.
  `k`를 인자로 열어 둔 것은 7-2 논스 재사용 실험용.
- `ecdsa_check.py` — s71-code2 "확인" 네 줄 + 고정 키로 DER 구조 뜯어 보기
- `cross_check.py` — coincurve(libsecp256k1)와 양방향 교차 확인 (`pip install coincurve`; lib은 표준 라이브러리만 쓴다)

## 실습 순서
1. `sign`·`verify`를 작성하고 확인 네 줄 실행: 정상 True · 메시지 변조 False · s → n − s도 True(수학적으로 유효 = low-S가 정책으로 필요한 이유) · DER 길이.
2. `der`를 작성하고 구조를 뜯어 본다.
3. 라이브러리 서명 → 내 verify, 내 DER → 라이브러리.
4. 6-1 실행기의 `checksig` 인자에 이 verify를 연결할 준비. 실제 트랜잭션의 z(서명 해시)는 7-4에서 (`part3/lesson-31/checksig_p2pkh.py`).

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-28/ecdsa_check.py
python part3/lesson-28/cross_check.py      # coincurve 필요
```

## 기대 출력
`ecdsa_check.py` — 앞 네 줄은 무작위 키라 마지막 숫자(DER 길이)만 실행마다 다름(대개 70 또는 71), 나머지는 결정적
```
True
False
True
71 (실행마다 다름)

DER 71 B: 3045022100cdf8386530cd0e0140f190847da8b23a3a4cd9574699b1f3a6b83184a6a91e7a0220644355102655d730d57f5449be5a511049c429f0a485f51d442aa6ddb84f17f9
  30 45 | 02 21 r=00cdf8386530cd0e0140f190847da8b23a3a4cd9574699b1f3a6b83184a6a91e7a | 02 20 s=644355102655d730d57f5449be5a511049c429f0a485f51d442aa6ddb84f17f9
  r의 최상위 비트가 1 → 앞에 0x00: True · low-S(s ≤ n/2): True
  parse_der 왕복: True
  high-S(n − s)로 바꾼 DER 길이: 72 · n − s의 최상위 비트: 1
```

`cross_check.py` (결정적, coincurve 21.0.0으로 직접 실행한 값)
```
라이브러리 서명 → 내 verify : True
내 DER 서명 → 라이브러리     : True
RFC6979 서명 바이트 일치     : True
libsecp256k1 DER: 3044022100c236f2e05a519348d33850e2d30aadecffd4ef25ddc5a73ecd3d544d7e8e4aad021f4eab322b09ccbd186084328958c32d19c7dbddb42d04807c9063b6a57be04f
```
- libsecp256k1도 RFC6979 논스와 low-S를 쓰므로 같은 키·메시지면 우리 `sign_rfc6979`와 바이트까지 같다.
- low-S면 s에는 0x00이 붙지 않아 DER 본문은 최대 71바이트(+ sighash 1B = 72). 슬라이드 s71-der의 "71~73"은 high-S까지 포함한 옛 범위다(ERRATA s71-code2).

## 테스트
`python -m pytest tests/test_ecdsa.py` — 서명→검증 왕복, low-S, DER 모양·패딩·파싱, RFC6979가 BIP143 공식 예제 서명 12개를 바이트 단위로 재현, 논스 재사용 복원, coincurve 교차 확인(설치돼 있을 때).

## 퀴즈
`quiz/lesson-28.md`
