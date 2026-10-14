"""4-1 실습: lib/bip39.py 확인 순서 (s41-bits, s41-code1, s41-code2).

공개된 테스트 니모닉만 쓴다. 실제 자금에 쓰지 말 것.
실행: python part2/lesson-14/bip39_check.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import random
from lib.bip39 import WORDS, entropy_to_mnemonic, is_valid, mnemonic_to_seed, new_mnemonic

print("엔트로피  체크섬  합계  단어 수")
for ent_bits in (128, 160, 192, 224, 256):
    cs = ent_bits // 32
    print(f"{ent_bits:6}비트 {cs:4}비트 {ent_bits + cs:5}비트 {(ent_bits + cs) // 11:5}")

m = entropy_to_mnemonic(bytes(16))
print("\nentropy_to_mnemonic(bytes(16)) →", m)
seed = mnemonic_to_seed(m, "TREZOR")
EXPECTED = ("c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553"
            "1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04")
print('mnemonic_to_seed(m, "TREZOR") →', seed.hex())
print("공식 벡터와 일치:", seed.hex() == EXPECTED)
print('"trezor"(소문자)  →', mnemonic_to_seed(m, "trezor").hex()[:32] + "…")
print("is_valid(m):", is_valid(m))

# 앞 11단어를 고정하면 유효한 마지막 단어는 2,048개 중 몇 개인가
head = " ".join(m.split()[:11])
valid_last = [w for w in WORDS if is_valid(head + " " + w)]
print(f"\n유효한 마지막 단어: {len(valid_last)}개 / 2048 (예: {', '.join(valid_last[:5])} …)")

# 새 니모닉의 마지막 단어를 무작위로 바꿔 보기 — 16번 중 1번꼴로 True
nm = new_mnemonic(12)
print("\n새 니모닉:", nm)
trials = 160
hits = sum(is_valid(" ".join(nm.split()[:11] + [random.choice(WORDS)])) for _ in range(trials))
print(f"마지막 단어를 무작위로 {trials}번 바꿈: True {hits}번 (기대 약 {trials // 16}번)")
