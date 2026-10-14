"""lib/base58.py — Bitcoin Core base58_encode_decode.json 전체 + Base58Check."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.base58 import b58encode, b58decode, b58check_encode, b58check_decode

ROOT = pathlib.Path(__file__).resolve().parents[1]
VECTORS = json.load(open(ROOT / "data" / "base58_encode_decode.json"))


@pytest.mark.parametrize("hexdata,b58", VECTORS)
def test_core_vectors(hexdata, b58):
    assert b58encode(bytes.fromhex(hexdata)) == b58
    assert b58decode(b58) == bytes.fromhex(hexdata)


def test_check_roundtrip_and_typo():
    payload = bytes.fromhex("00751e76e8199196d454941c45d1b3a323f1433bd6")
    s = b58check_encode(payload)
    assert s == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"
    assert b58check_decode(s) == payload
    bad = s[:-1] + ("j" if s[-1] != "j" else "k")
    with pytest.raises(ValueError, match="체크섬"):
        b58check_decode(bad)


def test_invalid_character():
    for c in "0OIl":
        with pytest.raises(ValueError):
            b58decode("1" + c)
