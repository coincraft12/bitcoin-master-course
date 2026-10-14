"""3-3 실습: 개인키 1로 P2PKH·WIF 테스트 벡터 검증, 체크섬 오류 확인 (s33-code, s33-vectors).

개인키 1은 누구나 아는 키다. 이 주소로 절대 송금하지 말 것.
실행: python part2/lesson-11/address_vectors.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G
from lib.hashes import hash160
from lib.base58 import b58check_decode
from lib.keys import ser_compressed, ser_uncompressed, p2pkh_address, p2sh_address, wif

EXPECTED = [
    ("p2pkh_address(ser_compressed(G))", p2pkh_address(ser_compressed(G)), "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"),
    ("p2pkh_address(ser_uncompressed(G))", p2pkh_address(ser_uncompressed(G)), "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm"),
    ("wif(1)", wif(1), "KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn"),
]
for call, got, want in EXPECTED:
    print(f"{'OK ' if got == want else 'FAIL'} {call:38} {got}")

print("\nHASH160(압축 공개키):", hash160(ser_compressed(G)).hex())
print("비압축 WIF          :", wif(1, compressed=False))
print("regtest P2PKH       :", p2pkh_address(ser_compressed(G), 0x6f))
print("regtest WIF         :", wif(1, version=0xef))
# P2SH: 스크립트의 HASH160을 버전 0x05로. 예로 <압축 G> OP_CHECKSIG (P2PK 스크립트)를 감싼다.
p2pk = bytes([0x21]) + ser_compressed(G) + b"\xac"
print("P2SH(P2PK 스크립트) :", p2sh_address(p2pk))

# 체크섬: 한 글자만 바꿔도 거부된다
addr = EXPECTED[0][1]
typo = addr[:10] + ("Z" if addr[10] != "Z" else "Y") + addr[11:]
print("\n원래 주소 :", addr)
print("오타 주소 :", typo)
try:
    b58check_decode(typo)
    print("결과      : 통과 (약 43억분의 1 확률)")
except ValueError as e:
    print("결과      :", e)
