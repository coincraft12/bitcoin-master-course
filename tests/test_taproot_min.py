"""lib/taproot.py (6-4 최소판) — BIP86 벡터로 출력키·lift_x 확인. 6강에서 테스트가 늘어난다."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from lib.ec import G, FIELD_P, point_mul
from lib.taproot import tagged_hash, lift_x, output_key
from lib import segwit_addr


def test_bip86_first_receive():
    P = bytes.fromhex("cc8a4bc64d897bddc5fbc2f670f7a8ba0b386779106cf1223c6fc5d7cd6fc115")
    Q = output_key(P)
    assert Q.hex() == "a60869f0dbcf1dc659c9cecbaf8050135ea9e8cdc487053f1dc6880949dc684c"
    assert segwit_addr.encode("bc", 1, Q) == "bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr"


def test_lift_x_even():
    P = lift_x(G[0])
    assert P[0] == G[0] and P[1] % 2 == 0
    with pytest.raises(ValueError):
        lift_x(7)
