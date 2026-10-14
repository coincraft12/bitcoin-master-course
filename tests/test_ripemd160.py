"""lib/ripemd160.py — 공식 RIPEMD-160 참조 벡터(Dobbertin·Bosselaers·Preneel 1996)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from lib.ripemd160 import ripemd160

VECTORS = [
    (b"", "9c1185a5c5e9fc54612808977ee8f548b2258d31"),
    (b"a", "0bdc9d2d256b3ee9daae347be6f4dc835a467ffe"),
    (b"abc", "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc"),
    (b"message digest", "5d0689ef49d2fae572b881b123a85ffa21595f36"),
    (b"abcdefghijklmnopqrstuvwxyz", "f71c27109c692c1b56bbdceb5b9d2865b3708dbc"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "12a053384a9c0c88e405a06c27dcf49ada62eb2b"),
    (b"1234567890" * 8, "9b752e45573d4b39f4dbd3323cab82bf63326bfb"),
]


@pytest.mark.parametrize("data,expected", VECTORS)
def test_reference_vectors(data, expected):
    assert ripemd160(data).hex() == expected


def test_million_a():
    assert ripemd160(b"a" * 1_000_000).hex() == "52783243c1697bdbe16d37f97f68f08325dc1528"


def test_returns_20_bytes_and_block_boundaries():
    for n in (55, 56, 63, 64, 65, 119, 120):      # 패딩이 바뀌는 경계
        assert len(ripemd160(b"x" * n)) == 20
