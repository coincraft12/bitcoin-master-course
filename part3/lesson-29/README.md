# lesson-29 · 7-2 논스 재사용 공격: 개인키 복원, 사고 연표, RFC6979·anti-exfil

## 목표
- 같은 논스 k로 만든 두 서명에서 개인키를 계산한다: k = (z₁ − z₂)/(s₁ − s₂), d = (s₁·k − z₁)/r (mod n).
- 논스 관련 실제 사고(2010 고정 k 펌웨어 서명 키, 2013 안드로이드 SecureRandom 결함, r 중복을 찾는 자동화 봇)와 원인을 설명한다.
- RFC6979 결정적 논스와 하드웨어 지갑의 anti-exfil 대책을 설명한다.

## 코드
- `nonce_reuse.py` — s72-code 그대로의 공격 + RFC6979 재실험. 기본은 **결정적**(고정 개인키·고정 k)이고 `--random`이면 슬라이드처럼 secrets로 뽑는다.
- `lib/ecdsa.py`에 이 차시에 추가하는 것: `rfc6979_nonce(d, z)`(RFC 6979 3.2절 HMAC-SHA256), `sign_rfc6979(d, z)`.
  BIP143 공식 예제 서명 12개를 바이트 단위로 재현한다(`tests/test_ecdsa.py`) — Bitcoin Core(libsecp256k1)가 쓰는 논스 규칙과 같다는 뜻.

## 실습 순서
1. 7-1에서 열어 둔 `sign(d, z, k)`로 일부러 같은 k를 두 번 쓴다 → `assert r1 == r2`(공격자가 찾는 단서).
2. `recover`: low-S 정규화로 s 부호가 바뀌었을 수 있어 (±s₁, ±s₂) 네 조합을 시도하고, 계산한 d로 공개키를 다시 만들어 확인.
3. RFC6979 논스로 다시: r이 달라 단서가 없다. 같은 메시지를 두 번 서명하면 같은 서명 — 안전하다(두 식을 빼도 얻을 정보가 없다).

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-29/nonce_reuse.py
python part3/lesson-29/nonce_reuse.py --random
```

## 기대 출력
기본 실행 (결정적, 직접 실행한 값 · 공개된 고정 데모 키)
```
== 같은 k로 두 메시지에 서명 ==
r1 == r2 (단서): True r = 13218ab300556daf4ebe11a3ee646cf854cfe4cd402e9363caa7e46b944d5218
True
원래 개인키  : 2b4875952406e33718023d713314833f8896daa8b53206548fd9f5e68a07a116
복원한 개인키: 2b4875952406e33718023d713314833f8896daa8b53206548fd9f5e68a07a116

== RFC6979 논스로 다시 ==
r1 == r2: False → 단서가 없다
같은 방법으로 복원 시도: False
같은 메시지 두 번 = 같은 서명: True (안전: 두 식을 빼도 얻을 정보가 없다)
```
`--random`은 r 값과 개인키 출력이 빠지고, 나머지 True/False는 같다.

## 퀴즈
`quiz/lesson-29.md`
