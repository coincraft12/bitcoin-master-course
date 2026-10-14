"""lib/sighash.py — 레거시(Core sighash.json 500개), BIP143 공식 예제 13개, BIP341 키 경로 7개 (7-4)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.tx import parse_tx
from lib.hashes import hash160
from lib.keys import parse_pubkey
from lib.script import parse_script
from lib.sighash import taproot_sighash, bip143_sighash, legacy_sighash, p2wpkh_script_code, outpoint, ser_out
from lib.ecdsa import verify, parse_der
from lib import schnorr

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
LEGACY = json.load(open(DATA / "sighash.json"))[1:]
B143 = json.load(open(DATA / "bip143_examples.json"))["examples"]
B341 = json.load(open(DATA / "bip341_wallet_test_vectors.json"))["keyPathSpending"][0]


@pytest.mark.parametrize("raw,script,idx,hash_type,expected", LEGACY)
def test_legacy_core_vectors(raw, script, idx, hash_type, expected):
    tx = parse_tx(raw)
    assert legacy_sighash(tx, idx, bytes.fromhex(script), hash_type)[::-1].hex() == expected


@pytest.mark.parametrize("e", B143, ids=[f"{e['section']}-{e['hash_type']}" for e in B143])
def test_bip143_examples(e):
    tx = parse_tx(e["unsigned_tx"])
    h = bip143_sighash(tx, e["input_index"], bytes.fromhex(e["script_code"]), e["amount_sat"], e["hash_type"])
    assert h.hex() == e["sighash"]
    sig = bytes.fromhex(e["signature"])
    assert sig[-1] == e["hash_type"]
    r, s = parse_der(sig[:-1])
    assert verify(parse_pubkey(bytes.fromhex(e["pubkey"])), int.from_bytes(h, "big"), r, s)


def test_bip143_p2wpkh_script_code():
    e = B143[0]                    # Native P2WPKH: scriptCode = 76a914{HASH160(공개키)}88ac
    assert p2wpkh_script_code(hash160(bytes.fromhex(e["pubkey"]))).hex() == e["script_code"]


def test_bip143_amount_matters():
    e = B143[0]
    tx = parse_tx(e["unsigned_tx"])
    sc = bytes.fromhex(e["script_code"])
    assert bip143_sighash(tx, 1, sc, e["amount_sat"] + 1).hex() != e["sighash"]    # s74-amount


@pytest.mark.parametrize("inp", B341["inputSpending"], ids=lambda i: f"in{i['given']['txinIndex']}-ht{i['given']['hashType']}")
def test_bip341_keypath_sighash(inp):
    tx = parse_tx(B341["given"]["rawUnsignedTx"])
    prev = [(u["amountSats"], bytes.fromhex(u["scriptPubKey"])) for u in B341["given"]["utxosSpent"]]
    g = inp["given"]
    msg = taproot_sighash(tx, prev, g["txinIndex"], g["hashType"])
    assert msg.hex() == inp["intermediary"]["sigHash"]
    # 공식 witness의 서명이 출력키에 대해 검증되는지 (s74-lab2와 같은 흐름)
    sig = bytes.fromhex(inp["expected"]["witness"][0])
    hash_type = sig[64] if len(sig) == 65 else 0x00
    assert hash_type == g["hashType"]
    out_key = prev[g["txinIndex"]][1][2:]
    assert schnorr.verify(msg, out_key, sig[:64])


def test_bip341_intermediary_hashes():
    from lib.sighash import sha
    tx = parse_tx(B341["given"]["rawUnsignedTx"])
    utxos = B341["given"]["utxosSpent"]
    i = B341["intermediary"]
    assert sha(b"".join(outpoint(x) for x in tx["vin"])).hex() == i["hashPrevouts"]
    assert sha(b"".join(u["amountSats"].to_bytes(8, "little") for u in utxos)).hex() == i["hashAmounts"]
    assert sha(b"".join(ser_out(o) for o in tx["vout"])).hex() == i["hashOutputs"]


def test_scope_default_vs_none():
    # s74-lab3: 출력 금액을 바꾸면 DEFAULT 메시지는 달라지고 NONE은 그대로 (백지수표)
    tx = parse_tx(B341["given"]["rawUnsignedTx"])
    prev = [(u["amountSats"], bytes.fromhex(u["scriptPubKey"])) for u in B341["given"]["utxosSpent"]]
    m_default = taproot_sighash(tx, prev, 0, 0x00)
    m_none = taproot_sighash(tx, prev, 0, 0x02)
    tx["vout"][0]["value_sat"] += 1_000_000
    assert taproot_sighash(tx, prev, 0, 0x00) != m_default
    assert taproot_sighash(tx, prev, 0, 0x02) == m_none


def test_block170_satoshi_signature():
    # T-02(블록 170)의 서명을 블록 9 코인베이스 출력(P2PK)으로 검증: 레거시 sighash + ECDSA
    t = parse_tx((DATA / "T-02.hex").read_text().strip())
    p = parse_tx((DATA / "T-02_prev.hex").read_text().strip())
    spk = bytes.fromhex(p["vout"][0]["scriptPubKey"])
    sig = parse_script(bytes.fromhex(t["vin"][0]["scriptSig"]))[0]
    pub = parse_script(spk)[0]
    z = int.from_bytes(legacy_sighash(t, 0, spk, sig[-1]), "big")
    r, s = parse_der(sig[:-1])
    assert verify(parse_pubkey(pub), z, r, s)
    assert not verify(parse_pubkey(pub), z + 1, r, s)
