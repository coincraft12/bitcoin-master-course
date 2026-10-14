"""lib/keys.py — 3강 슬라이드 벡터, Core key_io_valid.json(WIF·주소 전체), 공개키 파싱."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.ec import FIELD_P, G, N, point_mul, is_on_curve
from lib.keys import (new_private_key, public_key, ser_uncompressed, ser_compressed, ser_xonly,
                      parse_pubkey, parse_xonly, p2pkh_address, p2sh_address, wif, parse_wif,
                      p2wpkh_address, p2wsh_address, p2sh_p2wpkh_address, p2tr_address,
                      address_to_script_pubkey)

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEY_IO = json.load(open(ROOT / "data" / "key_io_valid.json", encoding="utf-8"))
EX = json.load(open(ROOT / "data" / "lesson03_examples.json", encoding="utf-8"))
WIF_VERSION = {"main": 0x80, "testnet4": 0xef, "signet": 0xef, "regtest": 0xef}


def test_slide_vectors_key1():
    assert p2pkh_address(ser_compressed(G)) == EX["p2pkh_compressed"]
    assert p2pkh_address(ser_uncompressed(G)) == EX["p2pkh_uncompressed"]
    assert wif(1) == EX["wif_compressed"]
    assert wif(1, compressed=False) == EX["wif_uncompressed"]
    assert p2wpkh_address(ser_compressed(G)) == EX["p2wpkh"]


def test_formats_and_parse():
    for _ in range(5):
        d = new_private_key()
        assert 1 <= d < N
        Q = public_key(d)
        assert (len(ser_uncompressed(Q)), len(ser_compressed(Q)), len(ser_xonly(Q))) == (65, 33, 32)
        assert parse_pubkey(ser_compressed(Q)) == Q
        assert parse_pubkey(ser_uncompressed(Q)) == Q
        X = parse_xonly(ser_xonly(Q))
        assert X[0] == Q[0] and X[1] % 2 == 0


def test_parse_rejects():
    with pytest.raises(ValueError):
        parse_pubkey(b"\x02" + FIELD_P.to_bytes(32, "big"))          # x 범위 초과
    with pytest.raises(ValueError):
        parse_pubkey(b"\x05" + bytes(32))                             # 알 수 없는 형식
    # x = 7 은 곡선 위의 점이 아니다 (BIP32 벡터 5의 무효 공개키)
    with pytest.raises(ValueError, match="곡선"):
        parse_pubkey(bytes.fromhex("02" + "00" * 31 + "07"))
    bad = ser_uncompressed(G)[:-1] + bytes([ser_uncompressed(G)[-1] ^ 1])
    with pytest.raises(ValueError, match="곡선"):
        parse_pubkey(bad)


@pytest.mark.parametrize("s,payload,meta", [v for v in KEY_IO if v[2]["isPrivkey"]])
def test_core_wif(s, payload, meta):
    d = int(payload, 16)
    assert wif(d, meta["isCompressed"], WIF_VERSION[meta["chain"]]) == s
    assert parse_wif(s) == (d, meta["isCompressed"], WIF_VERSION[meta["chain"]])


@pytest.mark.parametrize("addr,spk,meta", [v for v in KEY_IO if not v[2]["isPrivkey"]])
def test_core_addresses(addr, spk, meta):
    assert address_to_script_pubkey(addr).hex() == spk


def test_p2sh_and_nested():
    # BIP49 테스트넷 벡터: m/49'/1'/0'/0/0 공개키 → 2Mww8dCYPUpKHofjgcXcBCEGmniw9CoaiD2
    v = json.load(open(ROOT / "data" / "bip_derivation_vectors.json", encoding="utf-8"))["bip49_testnet"]
    assert p2sh_p2wpkh_address(bytes.fromhex(v["pubkey_hex"]), 0xc4) == v["address"]
    assert p2sh_address(b"\x00\x14" + bytes(20)).startswith("3")


def test_p2wsh_and_p2tr_encoding():
    # BIP173 벡터: P2WSH tb1qrp33g0q5c5… 의 witness script = <압축 G> OP_CHECKSIG
    ws = bytes([0x21]) + ser_compressed(G) + b"\xac"
    assert p2wsh_address(ws, "tb") == "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7"
    # BIP350 벡터: v1 프로그램 = G의 x좌표
    assert p2tr_address(ser_xonly(G)) == "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0"
    with pytest.raises(ValueError):
        p2tr_address(ser_compressed(G))
