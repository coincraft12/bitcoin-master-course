"""lib/bip32.py — BIP32 공식 벡터 1~5 전체, 일반·강화 파생, xpub 공격, BIP84/BIP86 경로 벡터."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.ec import G, N, point_mul
from lib.keys import ser_compressed, p2wpkh_address, p2pkh_address, p2sh_p2wpkh_address, p2tr_address
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import (HARD, hmac512, master, ckd_priv, ckd_pub, parse_path, derive_priv, derive_pub,
                       derive_ext, derive_xprv, derive_xpub, fingerprint, serialize, parse_extended, neuter)
from lib.taproot import output_key

ROOT = pathlib.Path(__file__).resolve().parents[1]
B32 = json.load(open(ROOT / "data" / "bip32_vectors.json"))
DV = json.load(open(ROOT / "data" / "bip_derivation_vectors.json"))
CASES = [(v["vector"], v["seed"], ch) for v in B32["vectors"] for ch in v["chains"]]


@pytest.mark.parametrize("vec,seed,chain", CASES, ids=[f"v{c[0]}-{c[2]['path']}" for c in CASES])
def test_official_chain(vec, seed, chain):
    sd = bytes.fromhex(seed)
    assert derive_xprv(sd, chain["path"]) == chain["xprv"]
    assert derive_xpub(sd, chain["path"]) == chain["xpub"]
    assert neuter(chain["xprv"]) == chain["xpub"]
    e = parse_extended(chain["xprv"])
    assert serialize(e["key"], e["chain_code"], e["depth"], e["parent_fp"], e["child"]) == chain["xprv"]


@pytest.mark.parametrize("item", B32["invalid"], ids=[i["reason"] for i in B32["invalid"]])
def test_vector5_invalid(item):
    with pytest.raises(ValueError):
        parse_extended(item["key"])


def test_master_fingerprint_vector1():
    k, _ = master(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
    assert fingerprint(point_mul(G, k)).hex() == "3442193e"


def test_ckd_pub_matches_ckd_priv():
    sd = bytes.fromhex(B32["vectors"][1]["seed"])
    k, c = master(sd)
    for i in (0, 1, 7, HARD - 1):
        kc, cc = ckd_priv(k, c, i)
        Kc, cc2 = ckd_pub(point_mul(G, k), c, i)
        assert point_mul(G, kc) == Kc and cc == cc2
    with pytest.raises(ValueError):
        ckd_pub(point_mul(G, k), c, HARD)


def test_xpub_child_derivation_vector2():
    # 벡터 2: m/0 xpub에서 일반 파생으로는 m/0/2147483647h 를 만들 수 없지만,
    # m/0/2147483647h/1 의 xpub에서 /2147483646h 는 막혀야 한다.
    v = B32["vectors"][1]["chains"]
    e = parse_extended(v[2]["xpub"])           # m/0/2147483647h
    K, c = derive_pub(e["key"], e["chain_code"], "1")
    assert serialize(K, c, e["depth"] + 1, fingerprint(e["key"]), 1) == v[3]["xpub"]
    with pytest.raises(ValueError):
        derive_pub(e["key"], e["chain_code"], "1/2147483646h")


def test_parse_path():
    assert parse_path("m/84h/1'/0H/0/5") == [84 + HARD, 1 + HARD, HARD, 0, 5]
    assert parse_path("m") == []
    with pytest.raises(ValueError):
        parse_path(f"m/{HARD}")


def test_recover_parent_attack():
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    k_par, c_par = derive_priv(seed, "m/84h/1h/0h")
    K_par = point_mul(G, k_par)
    k_child, _ = ckd_priv(k_par, c_par, 5)
    I = hmac512(c_par, ser_compressed(K_par) + (5).to_bytes(4, "big"))
    assert (k_child - int.from_bytes(I[:32], "big")) % N == k_par


def test_bip84_vectors():
    v = DV["bip84"]
    seed = mnemonic_to_seed(v["mnemonic"])
    for a in v["addresses"]:
        pub = ser_compressed(point_mul(G, derive_priv(seed, a["path"])[0]))
        assert pub.hex() == a["pubkey"]
        assert p2wpkh_address(pub) == a["address"]


def test_bip86_vectors():
    v = DV["bip86"]
    seed = mnemonic_to_seed(v["mnemonic"])
    assert derive_xprv(seed, "m") == v["rootpriv"]
    for a in v["addresses"]:
        assert derive_xprv(seed, a["path"]) == a["xprv"]
        assert derive_xpub(seed, a["path"]) == a["xpub"]
        P = point_mul(G, derive_priv(seed, a["path"])[0])
        assert P[0].to_bytes(32, "big").hex() == a["internal_key"]
        Q = output_key(P[0].to_bytes(32, "big"))
        assert Q.hex() == a["output_key"]
        assert p2tr_address(Q) == a["address"]


def test_bip49_testnet_vector():
    v = DV["bip49_testnet"]
    seed = mnemonic_to_seed(v["mnemonic"])
    k, _ = derive_priv(seed, v["path"])
    assert k.to_bytes(32, "big").hex() == v["privkey_hex"]
    assert p2sh_p2wpkh_address(ser_compressed(point_mul(G, k)), 0xc4) == v["address"]


def test_lesson16_slide_table():
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    pub = lambda p: ser_compressed(point_mul(G, derive_priv(seed, p)[0]))
    assert p2pkh_address(pub("m/44h/0h/0h/0/0")) == "1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA"
    assert p2sh_p2wpkh_address(pub("m/49h/0h/0h/0/0")) == "37VucYSaXLCAsxYyAPfbSi9eh4iEcbShgf"
    assert p2wpkh_address(pub("m/84h/0h/0h/0/0")) == "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"


def test_testnet_serialization():
    seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    t = derive_xprv(seed, "m/84h/1h/0h", testnet=True)
    assert t.startswith("tprv") and parse_extended(t)["testnet"]
    assert neuter(t).startswith("tpub")
    k, c, depth, fp, child = derive_ext(seed, "m/84h/1h/0h")
    assert depth == 3 and child == HARD
