"""lib/segwit_addr.py — BIP173/BIP350 참조 테스트 벡터 전체 (data/bech32_vectors.json)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib import segwit_addr
from lib.segwit_addr import Encoding

ROOT = pathlib.Path(__file__).resolve().parents[1]
V = json.load(open(ROOT / "data" / "bech32_vectors.json", encoding="utf-8"))


def segwit_scriptpubkey(witver, witprog):
    return bytes([witver + 0x50 if witver else 0, len(witprog)] + witprog)


@pytest.mark.parametrize("spec,test", [(Encoding.BECH32, t) for t in V["VALID_BECH32"]] +
                                      [(Encoding.BECH32M, t) for t in V["VALID_BECH32M"]])
def test_valid_checksum(spec, test):
    hrp, _, dspec = segwit_addr.bech32_decode(test)
    assert hrp is not None and dspec == spec
    pos = test.rfind("1")
    test = test[:pos + 1] + chr(ord(test[pos + 1]) ^ 1) + test[pos + 2:]
    hrp, _, dspec = segwit_addr.bech32_decode(test)
    assert hrp is None


@pytest.mark.parametrize("spec,test", [(Encoding.BECH32, t) for t in V["INVALID_BECH32"]] +
                                      [(Encoding.BECH32M, t) for t in V["INVALID_BECH32M"]])
def test_invalid_checksum(spec, test):
    hrp, _, dspec = segwit_addr.bech32_decode(test)
    assert hrp is None or dspec != spec


@pytest.mark.parametrize("address,hexscript", V["VALID_ADDRESS"])
def test_valid_address(address, hexscript):
    hrp = "bc"
    witver, witprog = segwit_addr.decode(hrp, address)
    if witver is None:
        hrp = "tb"
        witver, witprog = segwit_addr.decode(hrp, address)
    assert witver is not None, address
    assert segwit_scriptpubkey(witver, witprog) == bytes.fromhex(hexscript)
    assert segwit_addr.encode(hrp, witver, witprog) == address.lower()


@pytest.mark.parametrize("test", V["INVALID_ADDRESS"])
def test_invalid_address(test):
    assert segwit_addr.decode("bc", test) == (None, None)
    assert segwit_addr.decode("tb", test) == (None, None)


@pytest.mark.parametrize("hrp,version,length", V["INVALID_ADDRESS_ENC"])
def test_invalid_address_enc(hrp, version, length):
    assert segwit_addr.encode(hrp, version, [0] * length) is None


def test_case_rules():
    a = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
    assert segwit_addr.decode("bc", a.upper()) != (None, None)      # 전부 대문자는 유효
    mixed = a[:10] + a[10:].upper()
    assert segwit_addr.decode("bc", mixed) == (None, None)          # 대소문자 혼합은 무효
