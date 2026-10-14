"""lib/hashes.py · lib/ripemd160.py — 알려진 값 대조."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import hashlib
import pytest
from lib.ripemd160 import ripemd160
from lib.hashes import sha256, dsha256, hash256, hash160, tagged_hash

# RIPEMD160 공식 테스트 벡터 (Bosselaers 페이지, Core ripemd160.py 자체 테스트와 같은 목록)
RIPEMD = [
    (b"", "9c1185a5c5e9fc54612808977ee8f548b2258d31"),
    (b"a", "0bdc9d2d256b3ee9daae347be6f4dc835a467ffe"),
    (b"abc", "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc"),
    (b"message digest", "5d0689ef49d2fae572b881b123a85ffa21595f36"),
    (b"abcdefghijklmnopqrstuvwxyz", "f71c27109c692c1b56bbdceb5b9d2865b3708dbc"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "12a053384a9c0c88e405a06c27dcf49ada62eb2b"),
    (b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", "b0e20b6e3116640286ed3a87a5713079b21f5189"),
    (b"1234567890" * 8, "9b752e45573d4b39f4dbd3323cab82bf63326bfb"),
]


@pytest.mark.parametrize("msg,out", RIPEMD)
def test_ripemd160_vectors(msg, out):
    assert ripemd160(msg).hex() == out


def test_ripemd160_million_a():
    assert ripemd160(b"a" * 1000000).hex() == "52783243c1697bdbe16d37f97f68f08325dc1528"


def test_ripemd160_matches_hashlib_if_available():
    try:
        h = hashlib.new("ripemd160")
    except ValueError:
        pytest.skip("이 환경의 hashlib에는 ripemd160이 없음 (OpenSSL 3)")
    for n in range(0, 300, 7):
        data = bytes(range(256))[:n] * 3
        h = hashlib.new("ripemd160", data)
        assert ripemd160(data) == h.digest()


def test_hash160_generator_compressed():
    # 개인키 1의 압축 공개키 → BIP173 벡터 bc1qw508d6… 의 witness program
    pub = bytes.fromhex("0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798")
    assert hash160(pub).hex() == "751e76e8199196d454941c45d1b3a323f1433bd6"


def test_sha256_family():
    assert sha256(b"").hex() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert dsha256(b"") == sha256(sha256(b""))
    assert hash256 is dsha256


def test_tagged_hash_definition():
    t = hashlib.sha256(b"TapTweak").digest()
    assert tagged_hash("TapTweak", b"x") == hashlib.sha256(t + t + b"x").digest()
