"""lib/script.py — 디코더와 간이 실행기의 P2PKH 추적 (6-1), 진짜 checksig 연결 (7-4)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
from lib.script import parse_script, run, is_true
from lib.tx import parse_tx
from lib.sighash import legacy_sighash
from lib.ecdsa import verify, parse_der
from lib.keys import parse_pubkey

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
DEMO = json.load(open(DATA / "demo_txs.json"))["txs"]["p2pkh"]
SPEND = parse_tx(DEMO["hex"])
SCRIPT_SIG = bytes.fromhex(SPEND["vin"][0]["scriptSig"])
SPK = bytes.fromhex(DEMO["prev"]["scriptPubKey"])


def test_parse_script_p2pkh():
    items = parse_script(SPK)
    assert items[0:2] == ["OP_DUP", "OP_HASH160"] and items[3:] == ["OP_EQUALVERIFY", "OP_CHECKSIG"]
    assert isinstance(items[2], bytes) and len(items[2]) == 20
    assert parse_script(bytes([0x4c, 2, 0xab, 0xcd, 0xff])) == [b"\xab\xcd", "OP_UNKNOWN_0xff"]


def test_trace_seven_steps(capsys):
    assert run(SCRIPT_SIG, SPK) is True
    lines = capsys.readouterr().out.strip().splitlines()
    names = [ln.split("|")[0].strip() for ln in lines]
    assert names == ["PUSH 72B", "PUSH 33B", "OP_DUP", "OP_HASH160", "PUSH 20B", "OP_EQUALVERIFY", "OP_CHECKSIG"] \
        or names == ["PUSH 71B", "PUSH 33B", "OP_DUP", "OP_HASH160", "PUSH 20B", "OP_EQUALVERIFY", "OP_CHECKSIG"]
    assert lines[-1].endswith("01")


def test_wrong_pubkey_hash_fails():
    bad = SPK[:3] + bytes([SPK[3] ^ 1]) + SPK[4:]
    assert run(SCRIPT_SIG, bad, trace=False) is False


def test_real_checksig():
    def checksig(sig, pub):
        z = int.from_bytes(legacy_sighash(SPEND, 0, SPK, sig[-1]), "big")
        r, s = parse_der(sig[:-1])
        return verify(parse_pubkey(pub), z, r, s)
    assert run(SCRIPT_SIG, SPK, checksig=checksig, trace=False) is True
    SPEND2 = parse_tx(DEMO["hex"]); SPEND2["vout"][0]["value_sat"] += 1
    def checksig2(sig, pub):
        z = int.from_bytes(legacy_sighash(SPEND2, 0, SPK, sig[-1]), "big")
        return verify(parse_pubkey(pub), z, *parse_der(sig[:-1]))
    assert run(SCRIPT_SIG, SPK, checksig=checksig2, trace=False) is False


def test_split_execution_blocks_op_return_trick():
    # 2010년 버그: 해제 스크립트 OP_1 OP_RETURN은 분리 실행에서 잠금 조건을 건너뛰지 못한다
    assert run(bytes([0x01, 0x01, 0x6a]), SPK, trace=False) is False


def test_is_true():
    assert not is_true(b"") and not is_true(b"\x00\x00") and is_true(b"\x01")
