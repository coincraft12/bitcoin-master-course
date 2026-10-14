# lesson-15 · 4-2 HD 키 파생: BIP32 마스터 키, 일반·강화 파생, xpub 위험

## 목표
- 시드 → HMAC-SHA512("Bitcoin seed") → 마스터 개인키(앞 32B)와 체인코드(뒤 32B)를 설명한다.
- 일반 파생(i < 2³¹, 부모 공개키)과 강화 파생(i ≥ 2³¹, 0x00‖부모 개인키)을 구현하고 차이를 설명한다.
- 계정 xpub + 일반 파생 자식 개인키 하나 → 부모 개인키 복원을 시연한다.

## 만드는 코드 (`lib/bip32.py`)
- 슬라이드(s42-code1): `HARD`, `hmac512(key, data)`, `master(seed)`, `ckd_priv(k, c, i)`, `ckd_pub(K, c, i)`
- 저장소 코드(나레이션): `derive_priv(seed, path)` → (k, c), `serialize(…)` 78바이트 직렬화, `fingerprint(K)`
- 실습에서 확장한 것: `derive_ext(seed, path)` → (k, c, 깊이, 부모 지문, 자식 번호), `derive_xprv`, `derive_xpub`, `parse_extended`, `neuter`, `parse_path`, `derive_pub`

78바이트 = 버전 4 ‖ 깊이 1 ‖ 부모 지문 4 ‖ 자식 번호 4 ‖ 체인코드 32 ‖ 키 33 → Base58Check (xprv·xpub / tprv·tpub).

## 실습 순서 (s42-code2)
1. BIP32 공식 테스트 벡터 1(시드 000102…0f)로 m, m/0h의 xprv와 마스터 지문 3442193e 대조
2. 같은 부모에서 `ckd_priv` 자식의 공개키 == `ckd_pub` 결과 (일반 파생만). 강화 번호로 `ckd_pub` → 오류
3. 공격 시연: m/84h/1h/0h 계정 키와 5번 자식 개인키 → `recover_parent` True. 5h로는 식을 세울 수 없다

## 실행
```bash
python part2/lesson-15/bip32_vectors.py
python part2/lesson-15/ckd_pub_check.py
python part2/lesson-15/xpub_attack.py
python -m pytest -q tests/test_bip32.py        # 벡터 1~5 전체 (벡터 5 무효 키 16개 포함)
```

## 기대 출력 (모두 결정적)
`bip32_vectors.py`
```
마스터 지문: 3442193e
m     OK  xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi
      깊이 0, 부모 지문 00000000, 자식 번호 0x00000000
      xpub xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8
m/0h  OK  xprv9uHRZZhk6KAJC1avXpDAp4MDc3sQKNxDiPvvkX8Br5ngLNv1TxvUxt4cV1rGL5hj6KCesnDYUhd7oWgT11eZG7XnxHrnYeSvkzY7d2bhkJ7
      깊이 1, 부모 지문 3442193e, 자식 번호 0x80000000
      xpub xpub68Gmy5EdvgibQVfPdqkBBCHxA5htiqg55crXYuXoQRKfDBFA1WEjWgP6LHhwBZeNK1VTsfTFUHCdrfp1bgwQ9xv5ski8PX9rL2dZXvgGDnw
```
한 글자라도 다르면 직렬화 필드 순서, 깊이, 지문 계산을 다시 확인한다.

`ckd_pub_check.py`
```
자식 0: ckd_priv의 공개키 == ckd_pub 결과 → True
자식 1: ckd_priv의 공개키 == ckd_pub 결과 → True
자식 2: ckd_priv의 공개키 == ckd_pub 결과 → True
자식 3: ckd_priv의 공개키 == ckd_pub 결과 → True
자식 4: ckd_priv의 공개키 == ckd_pub 결과 → True
강화 번호 5h로 ckd_pub: 공개키로는 강화 파생 불가
```
`xpub_attack.py`
```
True
False
```
두 번째 줄: 강화 자식(5h)은 I = HMAC(c, 0x00‖부모 개인키‖i)라서 xpub만으로는 I를 계산할 수 없다. 공개키를 넣어 억지로 계산하면 틀린 값이 나온다.

## 퀴즈
`quiz/lesson-15.md`
