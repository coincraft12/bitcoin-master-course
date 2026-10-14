"""교육용 구현. 실제 자금에 쓰지 말 것.

BIP39 니모닉 (4-1): 엔트로피 → 니모닉 → 시드.

    from lib.bip39 import entropy_to_mnemonic, is_valid, mnemonic_to_seed, new_mnemonic

단어 목록은 BIP39 원문 저장소의 english.txt를 data/bip39_english.txt로 둔 것이다.
실습에서는 공개된 테스트 니모닉만 쓴다.
"""
import hashlib
import pathlib
import secrets
import unicodedata

# 슬라이드는 open("data/bip39_english.txt")로 저장소 최상위 기준 경로를 쓴다.
# 어느 폴더에서 실행해도 같은 파일을 읽도록 이 파일 기준으로 찾는다.
_WORDLIST = pathlib.Path(__file__).resolve().parents[1] / "data" / "bip39_english.txt"
WORDS = open(_WORDLIST, encoding="utf-8").read().split()


def nfkd(s: str) -> str:
    return unicodedata.normalize("NFKD", s)


def entropy_to_mnemonic(ent: bytes) -> str:
    cs_len = len(ent) * 8 // 32
    h = hashlib.sha256(ent).digest()
    bits = (int.from_bytes(ent, "big") << cs_len) | (h[0] >> (8 - cs_len))
    total = len(ent) * 8 + cs_len
    return " ".join(WORDS[(bits >> (total - 11 * (i + 1))) & 0x7FF] for i in range(total // 11))


def mnemonic_to_entropy(mnemonic: str) -> bytes:
    """니모닉 → 엔트로피. 체크섬은 검사하지 않는다(검사는 is_valid)."""
    ws = mnemonic.split()
    total = len(ws) * 11; cs_len = total // 33; bits = 0
    for w in ws: bits = (bits << 11) | WORDS.index(w)
    return (bits >> cs_len).to_bytes((total - cs_len) // 8, "big")


def is_valid(mnemonic: str) -> bool:
    ws = mnemonic.split()
    if len(ws) not in (12, 15, 18, 21, 24) or any(w not in WORDS for w in ws): return False
    total = len(ws) * 11; cs_len = total // 33; bits = 0
    for w in ws: bits = (bits << 11) | WORDS.index(w)
    ent = (bits >> cs_len).to_bytes((total - cs_len) // 8, "big")
    return entropy_to_mnemonic(ent) == " ".join(ws)


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    return hashlib.pbkdf2_hmac("sha512", nfkd(mnemonic).encode(),
                               ("mnemonic" + nfkd(passphrase)).encode(), 2048)


def new_mnemonic(words: int = 12) -> str:
    return entropy_to_mnemonic(secrets.token_bytes(words * 4 // 3))
