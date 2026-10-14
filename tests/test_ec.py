"""lib/ec.py — secp256k1 상수와 G·N 관계 점검 (3-1 확인 순서)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.ec import FIELD_P, N, G, is_on_curve, point_add, point_mul


def test_constants():
    assert FIELD_P == 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    assert FIELD_P % 4 == 3                      # 제곱근을 거듭제곱 한 번으로 (3-2)


def test_slide_checks():
    assert is_on_curve(G)
    assert point_mul(G, N) is None               # n·G = 무한원점
    assert point_mul(G, 2) == point_add(G, G)
    assert point_mul(G, 1) == G


def test_order_relations():
    minus_g = point_mul(G, N - 1)
    assert minus_g == (G[0], FIELD_P - G[1])     # (n-1)·G = −G
    assert point_add(minus_g, G) is None
    assert point_mul(G, N + 1) == G


def test_known_multiples():
    # 2G, 3G의 x좌표 (BIP340 테스트 벡터 0의 공개키가 3G의 x)
    assert point_mul(G, 2)[0] == 0xC6047F9441ED7D6D3045406E95C07CD85C778E4B8CEF3CA7ABAC09B95C709EE5
    assert point_mul(G, 3)[0] == 0xF9308A019258C31049344F85F89D5229B531C845836F99B08601F113BCE036F9


def test_linearity():
    a, b = 0x1234567890ABCDEF, 0xFEDCBA0987654321
    assert point_add(point_mul(G, a), point_mul(G, b)) == point_mul(G, a + b)
    assert is_on_curve(point_mul(G, a * b))
