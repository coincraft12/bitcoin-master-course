"""lib/schnorr.py — BIP340 공식 테스트 벡터 19개 전부(서명·검증) (7-3)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import csv
import pytest
from lib.schnorr import sign, verify, pubkey_gen

ROWS = list(csv.DictReader(open(pathlib.Path(__file__).resolve().parents[1] / "data" / "bip340_test_vectors.csv")))


def test_vector_count():
    assert len(ROWS) == 19


@pytest.mark.parametrize("row", ROWS, ids=[r["index"] for r in ROWS])
def test_bip340_vector(row):
    pubkey = bytes.fromhex(row["public key"])
    msg = bytes.fromhex(row["message"])
    sig = bytes.fromhex(row["signature"])
    expected = row["verification result"] == "TRUE"
    if row["secret key"]:
        seckey = bytes.fromhex(row["secret key"])
        assert pubkey_gen(seckey) == pubkey
        assert sign(msg, seckey, bytes.fromhex(row["aux_rand"])) == sig
    assert verify(msg, pubkey, sig) == expected


def test_tamper():
    row = ROWS[1]
    seckey, msg = bytes.fromhex(row["secret key"]), bytes.fromhex(row["message"])
    sig = sign(msg, seckey, b"\x00" * 32)
    pub = pubkey_gen(seckey)
    assert verify(msg, pub, sig)
    assert not verify(msg[:-1] + bytes([msg[-1] ^ 1]), pub, sig)
    assert not verify(msg, pub, sig[:63] + bytes([sig[63] ^ 1]))
    assert len(sig) == 64
