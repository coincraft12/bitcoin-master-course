"""3부 미니 과제 정답(lesson-31 solution)을 노드 없이 끝까지: 고정 키 + 가짜 UTXO → 서명된 Taproot 키 경로 송금."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "part3" / "lesson-31" / "assignment" / "solution"))
import solution_taproot_send as sol
from lib.tx import parse_tx


def test_offline_send(capsys):
    sol.offline()
    out = capsys.readouterr().out
    assert "txid 52f3d9ca6134e26bd276da5ea3bfaab0545d9c60bf65c481acfaa7004abb0119" in out
    hexstr = [l for l in out.splitlines() if l.startswith("05 ")][0].split()[-1]
    t = parse_tx(hexstr)
    assert t["vsize"] == 142 and [o["value_sat"] for o in t["vout"]] == [5_000_000, 4_999_290]


def test_signature_with_libsecp256k1(capsys):
    coincurve = pytest.importorskip("coincurve")
    sol.offline()
    lines = capsys.readouterr().out.splitlines()
    Q = bytes.fromhex([l for l in lines if "출력키" in l][0].split()[-1])
    msg = bytes.fromhex([l for l in lines if "서명 해시" in l][0].split()[-1])
    sig = bytes.fromhex([l for l in lines if l.strip().startswith("서명 ")][0].split()[-1])
    assert coincurve.PublicKeyXOnly(Q).verify(sig, msg)


def test_change_not_forgotten():
    utxo = {"txid": "11" * 32, "vout": 0, "value_sat": 10_000_000, "scriptPubKey": "5120" + "22" * 32}
    tx = sol.build_unsigned_tx(utxo, "bcrt1qp7shgcwx3mpzgxjvff0d77vuhchcldzfxnktde", 5_000_000,
                               "bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg", 5)
    assert len(tx["vout"]) == 2 and 10_000_000 - sum(o["value_sat"] for o in tx["vout"]) < 1_000
