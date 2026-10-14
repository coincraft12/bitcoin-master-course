"""lib/bip39.py — 공식 워드리스트와 BIP39 영어 테스트 벡터 전체 (trezor/python-mnemonic vectors.json)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import hashlib
import json
import pytest
from lib.bip39 import WORDS, entropy_to_mnemonic, mnemonic_to_entropy, is_valid, mnemonic_to_seed, new_mnemonic
from lib.bip32 import master, serialize

ROOT = pathlib.Path(__file__).resolve().parents[1]
VECTORS = json.load(open(ROOT / "data" / "bip39_vectors.json", encoding="utf-8"))["english"]


def test_wordlist():
    assert len(WORDS) == 2048 and len(set(WORDS)) == 2048
    assert WORDS[0] == "abandon" and WORDS[-1] == "zoo"
    raw = (ROOT / "data" / "bip39_english.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
    assert len({w[:4] for w in WORDS}) == 2048          # 앞 4글자로 모두 구분 (4-1)


@pytest.mark.parametrize("entropy,mnemonic,seed,xprv", VECTORS)
def test_official_vectors(entropy, mnemonic, seed, xprv):
    ent = bytes.fromhex(entropy)
    assert entropy_to_mnemonic(ent) == mnemonic
    assert mnemonic_to_entropy(mnemonic) == ent
    assert is_valid(mnemonic)
    s = mnemonic_to_seed(mnemonic, "TREZOR")
    assert s.hex() == seed
    k, c = master(s)
    assert serialize(k, c) == xprv


def test_invalid_mnemonics():
    m = entropy_to_mnemonic(bytes(16))
    assert not is_valid(m.replace("about", "abandon"))
    assert not is_valid(" ".join(m.split()[:11]))
    assert not is_valid(m.replace("about", "bitcoinx"))


def test_last_word_128_of_2048():
    head = " ".join(entropy_to_mnemonic(bytes(16)).split()[:11])
    assert sum(is_valid(head + " " + w) for w in WORDS) == 128


def test_passphrase_changes_seed():
    m = entropy_to_mnemonic(bytes(16))
    assert mnemonic_to_seed(m, "TREZOR") != mnemonic_to_seed(m, "trezor")
    assert mnemonic_to_seed(m) != mnemonic_to_seed(m, "TREZOR")


@pytest.mark.parametrize("n", [12, 15, 18, 21, 24])
def test_new_mnemonic(n):
    m = new_mnemonic(n)
    assert len(m.split()) == n and is_valid(m)
