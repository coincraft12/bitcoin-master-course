"""lib/taproot.py (6강 확장) — BIP341 wallet-test-vectors scriptPubKey 7개 전부:
내부키·트리 → 잎 해시·머클 루트·조정값·출력키·scriptPubKey·주소·컨트롤 블록, 그리고 키 경로 조정 개인키.
NUMS H, lift_x의 x ≥ FIELD_P 검사(7-3)도 확인한다. 6-4 최소판 테스트는 tests/test_taproot_min.py.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import json
import pytest
from lib.ec import G, N, FIELD_P, point_mul
from lib.taproot import (tagged_hash, lift_x, output_key, ser_compact, tapleaf_hash, tapbranch_hash,
                         verify_script_path, NUMS_H, nums_h, taproot_tree, tweak_pubkey, control_block,
                         p2tr_script_pubkey)
from lib import segwit_addr

V = json.load(open(pathlib.Path(__file__).resolve().parents[1] / "data" / "bip341_wallet_test_vectors.json", encoding="utf-8"))
SPK = V["scriptPubKey"]


@pytest.mark.parametrize("v", SPK, ids=[f"spk{i}" for i in range(len(SPK))])
def test_bip341_script_pubkey(v):
    g, i, e = v["given"], v["intermediary"], v["expected"]
    P = bytes.fromhex(g["internalPubkey"])
    leaves, root = taproot_tree(g["scriptTree"])
    if g["scriptTree"] is None:
        assert i["merkleRoot"] is None and root == b""
    else:
        assert [tapleaf_hash(s, lv).hex() for lv, s, _ in leaves] == i["leafHashes"]
        assert root.hex() == i["merkleRoot"]
    assert tagged_hash("TapTweak", P + root).hex() == i["tweak"]
    parity, Q = tweak_pubkey(P, root)
    assert Q.hex() == i["tweakedPubkey"] == output_key(P, root).hex()
    assert p2tr_script_pubkey(Q).hex() == e["scriptPubKey"]
    assert segwit_addr.encode("bc", 1, Q) == e["bip350Address"]
    cbs = [control_block(P, lv, path, root).hex() for lv, s, path in leaves]
    assert cbs == e.get("scriptPathControlBlocks", [])
    for (lv, s, _), cb in zip(leaves, cbs):
        assert verify_script_path(Q, s, bytes.fromhex(cb))
        assert len(bytes.fromhex(cb)) == 33 + 32 * ((len(cb) // 2 - 33) // 32)


def test_verify_script_path_rejects_wrong_leaf():
    v = SPK[3]                                  # 잎 2개
    P = bytes.fromhex(v["given"]["internalPubkey"])
    leaves, root = taproot_tree(v["given"]["scriptTree"])
    _, Q = tweak_pubkey(P, root)
    lv, s, path = leaves[0]
    cb = control_block(P, lv, path, root)
    assert verify_script_path(Q, s, cb)
    assert not verify_script_path(Q, s + b"\x51", cb)


def test_keypath_tweaked_privkeys():
    k = V["keyPathSpending"][0]
    for inp in k["inputSpending"]:
        g, i = inp["given"], inp["intermediary"]
        d0 = int(g["internalPrivkey"], 16)
        P = point_mul(G, d0)
        assert P[0].to_bytes(32, "big").hex() == i["internalPubkey"]
        root = bytes.fromhex(g["merkleRoot"]) if g["merkleRoot"] else b""
        t = int.from_bytes(tagged_hash("TapTweak", P[0].to_bytes(32, "big") + root), "big")
        assert t.to_bytes(32, "big").hex() == i["tweak"]
        d = d0 if P[1] % 2 == 0 else N - d0
        assert ((d + t) % N).to_bytes(32, "big").hex() == i["tweakedPrivkey"]


def test_nums_h():
    # s65-nums: H = lift_x(SHA256(G의 비압축 직렬화))
    assert nums_h() == NUMS_H
    assert NUMS_H.hex() == "50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0"


def test_lift_x_field_check():
    with pytest.raises(ValueError):
        lift_x(FIELD_P)                         # 7-3에서 추가한 검사
    with pytest.raises(ValueError):
        lift_x(FIELD_P + G[0])                  # mod p로는 G.x지만 범위 밖이면 거부


def test_ser_compact_and_branch_order():
    assert ser_compact(34) == b"\x22" and ser_compact(300) == b"\xfd\x2c\x01"
    a, b = b"\x01" * 32, b"\x02" * 32
    assert tapbranch_hash(a, b) == tapbranch_hash(b, a)       # 사전순 정렬 → 좌우 정보 불필요


def test_control_block_sizes():
    # s65-witness·s65-quiz: 깊이 1 → 65B, 깊이 2 → 97B
    leaf = lambda n: (bytes([0x51 + n]), 0xc0)
    leaves, root = taproot_tree([leaf(0), [leaf(1), leaf(2)]])
    sizes = [len(control_block(NUMS_H, lv, path, root)) for lv, s, path in leaves]
    assert sizes == [65, 97, 97]
