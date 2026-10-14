"""lib/block.py — 제네시스 헤더, bits↔target, 머클 루트·증명, 난이도 조정, 보조금 (10·11강).

데이터 출처는 data/SOURCES.md:
- data/genesis_blocks.json   Bitcoin Core v31.1 chainparams.cpp (인자로 조립, assert 해시로 검증)
- data/block100000.json      btcd btcutil/block_test.go (헤더 필드·txid 4개)
- data/pow_retarget_vectors.json  Bitcoin Core v31.1 src/test/pow_tests.cpp
- data/blockfilters.json     Bitcoin Core src/test/data/blockfilters.json (testnet3 실제 블록)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.block import (parse_header, bits_to_target, check_pow, merkle_root, mine, retarget,
                       POW_LIMIT, TWO_WEEKS, COIN, subsidy, total_supply, serialize_header,
                       header_hash, target_to_bits, difficulty, block_work, next_bits,
                       merkle_proof, root_from_proof, verify_merkle_proof, parse_merkleblock,
                       extract_matches, build_merkleblock, signals_bit)

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = json.load(open(ROOT / "data" / "genesis_blocks.json", encoding="utf-8"))
B100K = json.load(open(ROOT / "data" / "block100000.json", encoding="utf-8"))
POW_VECTORS = json.load(open(ROOT / "data" / "pow_retarget_vectors.json", encoding="utf-8"))["vectors"]
FILTERS = json.load(open(ROOT / "data" / "blockfilters.json", encoding="utf-8"))[1:]

GENESIS_HEADER = bytes.fromhex(GEN["main"]["header"])


# ── 10-1 헤더 ─────────────────────────────────────────────────────────────

def test_genesis_header_fields_and_hash():
    assert len(GENESIS_HEADER) == 80
    hdr = parse_header(GENESIS_HEADER)
    assert hdr["hash"] == "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
    assert hdr["hash"].startswith("000000000019d6")
    assert hdr["version"] == 1
    assert hdr["prev"] == "00" * 32
    assert hdr["merkle_root"] == "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
    assert hdr["time"] == 1231006505
    assert hdr["bits"] == 0x1d00ffff
    assert hdr["nonce"] == 2083236893
    assert check_pow(GENESIS_HEADER)
    assert header_hash(GENESIS_HEADER) == hdr["hash"]


def test_genesis_coinbase_txid_is_merkle_root():
    # 트랜잭션 1개인 블록의 머클 루트 = 그 txid
    assert merkle_root([GEN["coinbase_txid"]]) == GEN["main"]["merkle_root"]


@pytest.mark.parametrize("net", ["main", "testnet3", "signet", "regtest"])
def test_all_genesis_headers(net):
    h = bytes.fromhex(GEN[net]["header"])
    hdr = parse_header(h)
    assert hdr["hash"] == GEN[net]["hash"]
    assert check_pow(h)
    assert serialize_header(hdr) == h


def test_parse_header_requires_80_bytes():
    with pytest.raises(AssertionError):
        parse_header(GENESIS_HEADER[:79])


def test_tampered_header_fails_pow():
    bad = bytearray(GENESIS_HEADER)
    bad[76] ^= 1                                  # nonce 1비트
    assert not check_pow(bytes(bad))


@pytest.mark.parametrize("row", FILTERS, ids=[str(r[0]) for r in FILTERS])
def test_testnet3_block_headers(row):
    height, block_hash, block_hex = row[0], row[1], row[2]
    h = bytes.fromhex(block_hex)[:80]
    assert parse_header(h)["hash"] == block_hash
    assert check_pow(h)


# ── bits ↔ target, 난이도 ────────────────────────────────────────────────

def test_difficulty_one_target():
    t = bits_to_target(0x1d00ffff)
    assert t == 0xffff << 208 == POW_LIMIT
    assert hex(t) == "0x" + "ffff" + "0" * 52
    assert difficulty(0x1d00ffff) == 1.0
    assert block_work(0x1d00ffff) == 0x100010001     # 제네시스 chainwork


def test_regtest_target():
    assert bits_to_target(0x207fffff) == 0x7fffff << 232
    assert difficulty(0x207fffff) < 1


def test_bits_to_target_formula():
    # 타깃 = 가수 × 256^(지수 − 3)
    assert bits_to_target(0x1b04864c) == 0x04864c * 256 ** (0x1b - 3)


@pytest.mark.parametrize("bits", [0x1d00ffff, 0x207fffff, 0x1e0377ae, 0x1b04864c, 0x1c05a3f4,
                                  0x1d00d86a, 0x1c0168fd, 0x1d00e1fd, 0x1c387f6f])
def test_target_to_bits_roundtrip(bits):
    assert target_to_bits(bits_to_target(bits)) == bits


def test_target_to_bits_sign_bit():
    # 가수 최상위 비트가 켜지면 지수를 올린다 (GetCompact)
    assert target_to_bits(0x80) == 0x02008000
    assert target_to_bits(0xffff << 208) == 0x1d00ffff
    assert target_to_bits((1 << 224) - 1) == 0x1d00ffff     # Core powLimit 00000000ffff…ff


# ── 10-2 머클 ────────────────────────────────────────────────────────────

def test_block100000_merkle_root():
    assert len(B100K["txids"]) == 4
    assert merkle_root(B100K["txids"]) == B100K["merkle_root"]
    assert B100K["merkle_root"].startswith("f3e94742")
    hdr = parse_header(bytes.fromhex(B100K["header"]))
    assert hdr["hash"] == B100K["hash"] == "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506"
    assert hdr["merkle_root"] == B100K["merkle_root"]
    assert check_pow(bytes.fromhex(B100K["header"]))


def test_merkle_root_empty():
    with pytest.raises(ValueError):
        merkle_root([])


def test_merkle_odd_duplication_ambiguity():
    a, b, c = B100K["txids"][:3]
    assert merkle_root([a, b, c]) == merkle_root([a, b, c, c])   # CVE-2012-2459의 원인


@pytest.mark.parametrize("i", range(4))
def test_merkle_proof_block100000(i):
    txids = B100K["txids"]
    proof = merkle_proof(txids, i)
    assert len(proof) == 2
    assert verify_merkle_proof(txids[i], i, proof, B100K["merkle_root"])
    assert not verify_merkle_proof(txids[i], i ^ 1, proof, B100K["merkle_root"])


@pytest.mark.parametrize("n", [1, 2, 3, 5, 7, 16, 17])
def test_merkle_proof_sizes(n):
    txids = [bytes([k]) .hex() * 32 for k in range(n)]
    root = merkle_root(txids)
    for i in range(n):
        assert root_from_proof(txids[i], i, merkle_proof(txids, i)) == root


@pytest.mark.parametrize("match", [{0}, {1}, {3}, {0, 3}, {0, 1, 2, 3}])
def test_merkleblock_roundtrip(match):
    txids = B100K["txids"]
    hexproof = build_merkleblock(bytes.fromhex(B100K["header"]), txids, {txids[i] for i in match})
    pmt = parse_merkleblock(hexproof)
    assert parse_header(pmt["header"])["hash"] == B100K["hash"]
    root, found = extract_matches(pmt)
    assert root == B100K["merkle_root"]
    assert found == [(i, txids[i]) for i in sorted(match)]


def test_merkleblock_rejects_duplicate_right():
    a, b, c = B100K["txids"][:3]
    fake = build_merkleblock(bytes.fromhex(B100K["header"]), [a, b, c, c], {c})
    with pytest.raises(ValueError):
        extract_matches(parse_merkleblock(fake))


# ── 11-1 채굴과 난이도 조정 ──────────────────────────────────────────────

def test_mine_genesis_prefix_slide_table():
    prefix = GENESIS_HEADER[:76]
    nonce, h, _ = mine(prefix, 8)
    assert nonce == 236 and h.startswith("00")
    nonce, h, _ = mine(prefix, 12)
    assert nonce == 4200 and int(h, 16) < 1 << 244


@pytest.mark.parametrize("v", POW_VECTORS, ids=[v["name"] for v in POW_VECTORS])
def test_core_retarget_vectors(v):
    assert next_bits(v["old_bits"], v["first_block_time"], v["last_block_time"]) == v["expected_bits"]


def test_retarget_slide_cases():
    old = bits_to_target(0x1c05a3f4)
    week = 7 * 24 * 3600
    assert TWO_WEEKS == 2016 * 600 == 2 * week
    assert retarget(old, week) == old // 2                 # 1주 → 타깃 ×0.5 (난이도 약 2배)
    assert retarget(old, 4 * week) == old * 2              # 4주 → ×2
    assert retarget(old, 10 * week) == old * 4             # 10주 → 제한 ×4
    assert retarget(old, 1) == old // 4                    # 하한 ×1/4
    assert retarget(POW_LIMIT, 4 * week) == POW_LIMIT      # 최대 타깃을 넘지 않는다


# ── 11-2 보조금 ──────────────────────────────────────────────────────────

def test_subsidy_mainnet():
    assert subsidy(0) == 50 * COIN
    assert subsidy(209_999) == 50 * COIN
    assert subsidy(210_000) == 25 * COIN
    assert subsidy(840_000) == 312_500_000
    assert subsidy(840_000) / COIN == 3.125
    assert subsidy(1_050_000) == 156_250_000
    assert subsidy(6_929_999) == 1                         # 마지막 sat
    assert subsidy(6_930_000) == 0                         # 33번째 반감기
    assert subsidy(64 * 210_000) == 0


def test_total_supply():
    assert total_supply() == 2_099_999_997_690_000
    assert total_supply() / COIN == 20999999.9769
    assert total_supply() < 21_000_000 * COIN


def test_subsidy_regtest_150():
    assert [subsidy(h, 150) for h in (149, 150, 299, 300)] == [
        5_000_000_000, 2_500_000_000, 2_500_000_000, 1_250_000_000]
    assert total_supply(150) * 1400 == total_supply()


# ── 11-5 버전 비트 ───────────────────────────────────────────────────────

def test_signals_bit():
    assert signals_bit(0x30000000, 28)
    assert not signals_bit(0x20000000, 28)
    assert not signals_bit(1, 0)            # BIP9 이전 형식
    assert signals_bit(0x20000004, 2)       # Taproot 신호 비트
