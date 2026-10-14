# lesson-14 · 4-1 시드와 니모닉: BIP39, 체크섬, PBKDF2, 패스프레이즈

## 목표
- 엔트로피 → (SHA256 체크섬) → 11비트씩 단어 → PBKDF2-HMAC-SHA512 2048회 → 64바이트 시드 과정을 설명한다.
- 마지막 단어의 체크섬 원리를 설명하고 `is_valid`로 유효성을 검사한다.
- 패스프레이즈의 효과(다른 지갑)와 위험(잊으면 영구 손실, 틀려도 오류 없음)을 설명한다.

## 만드는 코드 (`lib/bip39.py`)
`WORDS`, `entropy_to_mnemonic(ent)`, `is_valid(mnemonic)`, `mnemonic_to_seed(mnemonic, passphrase="")`, `new_mnemonic(words=12)`, 보충 `mnemonic_to_entropy`, `nfkd`.
단어 목록은 BIP39 원문 저장소의 english.txt를 `data/bip39_english.txt`로 그대로 둔 것이다.

## 실습 순서 (s41-code1, s41-code2)
1. `entropy_to_mnemonic(bytes(16))` → abandon ×11 + about (BIP39 공식 벡터 첫 줄)
2. 같은 니모닉 + 패스프레이즈 `TREZOR` → 공식 벡터의 64바이트 시드와 일치
3. `trezor`(소문자)로 바꾸면 시드 전체가 달라진다
4. 마지막 단어를 바꾸면 `is_valid`는 대부분 False, 16번 중 1번꼴로 True (체크섬 4비트)

> 공개된 테스트 니모닉만 쓴다. 사람이 고른 단어 12개는 니모닉이 아니다.

## 실행
```bash
python part2/lesson-14/bip39_check.py
python -m pytest -q tests/test_bip39.py        # 공식 영어 벡터 전체
```

## 기대 출력
마지막 두 블록(새 니모닉, 무작위 실험)만 실행마다 다르다.
```
엔트로피  체크섬  합계  단어 수
   128비트    4비트   132비트    12
   160비트    5비트   165비트    15
   192비트    6비트   198비트    18
   224비트    7비트   231비트    21
   256비트    8비트   264비트    24

entropy_to_mnemonic(bytes(16)) → abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
mnemonic_to_seed(m, "TREZOR") → c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04
공식 벡터와 일치: True
"trezor"(소문자)  → f5057546039282b59dad6d6470999857…
is_valid(m): True

유효한 마지막 단어: 128개 / 2048 (예: about, actual, age, alpha, angle …)

새 니모닉: present public violin little tuition steak initial ladder media museum pact during (실행마다 다름)
마지막 단어를 무작위로 160번 바꿈: True 17번 (기대 약 10번) (실행마다 다름)
```
앞 11단어가 정해지면 유효한 마지막 단어는 2,048개 중 128개(= 2^7, 엔트로피 7비트)뿐이다.

## 퀴즈
`quiz/lesson-14.md`
