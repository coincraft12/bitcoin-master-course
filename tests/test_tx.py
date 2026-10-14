"""lib/tx.py — 파싱→직렬화 왕복, txid·wtxid·size·weight·vsize (5-2).

공식 데이터
- T-02: 블록 170 송금(f4184fc5…). 파일 해시가 슬라이드의 txid와 같다는 것 자체가 원본 증명
- Bitcoin Core src/test/data/sighash.json의 raw 트랜잭션 500개 (왕복)
- BIP143 예제의 서명 전·후 트랜잭션: 서명 전 레거시 형식 txid = 서명 후 SegWit 형식의 txid
- BIP341 wallet-test-vectors: 서명 전 트랜잭션에 공식 witness를 붙여도 txid는 그대로
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.tx import dsha256, read_varint, write_varint, parse_tx, serialize_tx

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
T02 = (DATA / "T-02.hex").read_text(encoding="utf-8").strip()
T02_PREV = (DATA / "T-02_prev.hex").read_text(encoding="utf-8").strip()


def test_varint_table():
    # s52-varint 표의 경계값
    for n, enc in [(0, "00"), (252, "fc"), (253, "fdfd00"), (65535, "fdffff"),
                   (65536, "fe00000100"), (2**32 - 1, "feffffffff"), (2**32, "ff0000000001000000")]:
        assert write_varint(n).hex() == enc
        assert read_varint(bytes.fromhex(enc), 0) == (n, len(enc) // 2)


def test_block170_t02():
    t = parse_tx(T02)
    assert t["txid"] == "f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16"
    assert t["wtxid"] == t["txid"]                       # 레거시: txid = wtxid
    assert not t["segwit"]
    assert (t["size"], t["weight"], t["vsize"]) == (275, 1100, 275)
    assert len(t["vin"]) == 1 and t["vin"][0]["vout"] == 0
    assert t["vin"][0]["txid"] == "0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9"
    assert [o["value_sat"] for o in t["vout"]] == [1_000_000_000, 4_000_000_000]   # 10 BTC, 40 BTC
    assert all(o["scriptPubKey"].startswith("41") and o["scriptPubKey"].endswith("ac") for o in t["vout"])  # P2PK


def test_block9_coinbase_fee_zero():
    p = parse_tx(T02_PREV)
    assert p["txid"] == "0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9"
    assert p["vin"][0]["txid"] == "00" * 32 and p["vin"][0]["vout"] == 0xffffffff   # 코인베이스
    t = parse_tx(T02)
    fee = p["vout"][0]["value_sat"] - sum(o["value_sat"] for o in t["vout"])
    assert fee == 0                                                                   # s51-lab2


def test_roundtrip_core_sighash_json():
    rows = json.load(open(DATA / "sighash.json", encoding="utf-8"))[1:]
    assert len(rows) == 500
    for raw, *_ in rows:
        t = parse_tx(raw)
        assert serialize_tx(t).hex() == raw
        assert t["wtxid"] == t["txid"] == dsha256(bytes.fromhex(raw))[::-1].hex()
        assert t["weight"] == 4 * len(raw) // 2


def test_bip143_signed_vs_unsigned():
    ex = json.load(open(DATA / "bip143_examples.json", encoding="utf-8"))["examples"]
    seen = set()
    for e in ex:
        if e["signed_tx"] is None or e["signed_tx"] in seen:
            continue
        seen.add(e["signed_tx"])
        s = parse_tx(e["signed_tx"])
        assert s["segwit"] and serialize_tx(s).hex() == e["signed_tx"]
        u = parse_tx(e["unsigned_tx"])
        # scriptSig가 빈 입력만 있던 예제는 서명 후에도 txid가 서명 전과 같다 (가변성 해결의 핵심)
        if all(i["scriptSig"] == "" for i in s["vin"]):
            assert s["txid"] == u["txid"]
        assert s["txid"] == dsha256(serialize_tx(s, include_witness=False))[::-1].hex()
        assert s["wtxid"] == dsha256(bytes.fromhex(e["signed_tx"]))[::-1].hex()
        assert s["wtxid"] != s["txid"]
        base = len(serialize_tx(s, include_witness=False))
        assert s["weight"] == base * 3 + s["size"] and s["vsize"] == (s["weight"] + 3) // 4
    assert len(seen) == 6


def test_bip341_witness_does_not_change_txid():
    v = json.load(open(DATA / "bip341_wallet_test_vectors.json", encoding="utf-8"))["keyPathSpending"][0]
    unsigned = v["given"]["rawUnsignedTx"]
    t = parse_tx(unsigned)
    for inp in v["inputSpending"]:
        t["vin"][inp["given"]["txinIndex"]]["witness"] = inp["expected"]["witness"]
    signed = serialize_tx(t).hex()
    s = parse_tx(signed)
    assert serialize_tx(s).hex() == signed
    assert s["txid"] == parse_tx(unsigned)["txid"] != s["wtxid"]
    assert s["size"] > len(unsigned) // 2 and s["vsize"] < s["size"]


def test_weight_example_slide():
    # s52-weight: base 110 · total 222 → 552 WU → 138 vB, s52-quiz: 200·300 → 225
    assert (110 * 3 + 222, (110 * 3 + 222 + 3) // 4) == (552, 138)
    assert (200 * 3 + 300 + 3) // 4 == 225


def test_trailing_bytes_rejected():
    with pytest.raises(AssertionError):
        parse_tx(T02 + "00")


def test_demo_txs_regenerate_identical():
    sys.path.insert(0, str(DATA))
    import make_demo_txs
    assert make_demo_txs.make() == json.load(open(DATA / "demo_txs.json", encoding="utf-8"))
    for k, t in make_demo_txs.make()["txs"].items():
        p = parse_tx(t["hex"])
        assert serialize_tx(p).hex() == t["hex"]
        assert t["prev"]["value_sat"] - sum(o["value_sat"] for o in p["vout"]) == t["fee_sat"] >= 5 * t["vsize"]
