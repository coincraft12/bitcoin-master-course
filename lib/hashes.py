"""교육용 구현. 실제 자금에 쓰지 말 것.

비트코인에서 쓰는 해시 함수 모음 (3-3).

    from lib.hashes import sha256, dsha256, hash256, hash160, tagged_hash

- sha256(b)       SHA256 한 번
- dsha256(b)      SHA256 두 번 (체크섬, txid, 블록 해시). hash256은 같은 함수의 다른 이름
- hash160(b)      RIPEMD160(SHA256(b)) — 공개키·스크립트 해시 (주소)
- tagged_hash     BIP340 태그 해시 SHA256(SHA256(tag)‖SHA256(tag)‖msg) — Taproot·Schnorr(6·7강)

RIPEMD160은 OpenSSL 3에서 hashlib으로 쓸 수 없는 경우가 많아 lib/ripemd160.py의
순수 Python 구현을 쓴다.
"""
import hashlib

from lib.ripemd160 import ripemd160


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def dsha256(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


hash256 = dsha256   # Bitcoin Core 용어 (HASH256 = SHA256d)


def hash160(b: bytes) -> bytes:
    return ripemd160(sha256(b))


def tagged_hash(tag: str, msg: bytes) -> bytes:
    t = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(t + t + msg).digest()
