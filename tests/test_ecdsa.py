"""lib/ecdsa.py — 서명→검증 왕복, low-S, DER, RFC6979 (7-1, 7-2).

RFC6979 공식 대조: BIP143 예제 12개의 서명은 Bitcoin Core(libsecp256k1, RFC6979 논스)가 만든 것이고,
개인키·sigHash·서명이 문서에 함께 있다 → sign_rfc6979가 바이트 단위로 같은 DER을 만들어야 한다.
coincurve(libsecp256k1 바인딩)가 설치돼 있으면 양방향 교차 확인도 한다(s71-code2).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import hashlib, json
import pytest
from lib.ec import G, N, point_mul
from lib.keys import ser_compressed, parse_pubkey
from lib.ecdsa import sign, verify, der, parse_der, rfc6979_nonce, sign_rfc6979

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
B143 = [e for e in json.load(open(DATA / "bip143_examples.json"))["examples"] if "privkey" in e]
D = int.from_bytes(hashlib.sha256(b"tests/test_ecdsa.py fixed key").digest(), "big") % N
Q = point_mul(G, D)
Z = int.from_bytes(hashlib.sha256(b"CoinCraft").digest(), "big")


def test_sign_verify_roundtrip():
    for _ in range(5):
        r, s = sign(D, Z)
        assert verify(Q, Z, r, s)
        assert not verify(Q, Z + 1, r, s)            # 메시지 변조
        assert verify(Q, Z, r, N - s)                # high-S도 수학적으로는 유효 (s71-code2)
        assert s <= N // 2                           # low-S


def test_verify_rejects_out_of_range():
    r, s = sign(D, Z)
    assert not verify(Q, Z, 0, s) and not verify(Q, Z, r, 0) and not verify(Q, Z, N, s)


def test_der_shape_and_parse():
    for i in range(20):
        z = int.from_bytes(hashlib.sha256(bytes([i])).digest(), "big")
        r, s = sign_rfc6979(D, z)
        sig = der(r, s)
        assert sig[0] == 0x30 and sig[1] == len(sig) - 2
        assert 68 <= len(sig) <= 71                  # low-S이면 s에 0x00 패딩이 붙지 않아 최대 71
        assert parse_der(sig) == (r, s)


def test_der_padding_rule():
    sig = der(0x80 << 248, 1)                        # 최상위 비트 1 → 0x00 덧붙임
    assert sig.hex() == "3026022100" + "80" + "00" * 31 + "020101"
    with pytest.raises(ValueError):
        parse_der(sig + b"\x01")                     # sighash 바이트를 떼지 않으면 형식 오류


@pytest.mark.parametrize("e", B143, ids=[f"{e['section']}-{e['hash_type']}" for e in B143])
def test_rfc6979_matches_bip143_signatures(e):
    d = int(e["privkey"], 16)
    assert ser_compressed(point_mul(G, d)).hex() == e["pubkey"]
    r, s = sign_rfc6979(d, int(e["sighash"], 16))
    assert der(r, s).hex() == e["signature"][:-2]


def test_rfc6979_deterministic():
    assert sign_rfc6979(D, Z) == sign_rfc6979(D, Z)
    assert rfc6979_nonce(D, Z) != rfc6979_nonce(D, Z + 1)
    assert 1 <= rfc6979_nonce(D, Z) < N


def test_nonce_reuse_recovers_key():
    # 7-2 s72-code: 같은 k로 두 메시지에 서명 → 개인키 복원
    h = lambda m: int.from_bytes(hashlib.sha256(m).digest(), "big")
    z1, z2 = h(b"pay Alice 1 BTC"), h(b"pay Bob 2 BTC")
    k = int.from_bytes(hashlib.sha256(b"reused k").digest(), "big") % N
    r1, s1 = sign(D, z1, k); r2, s2 = sign(D, z2, k)
    assert r1 == r2
    found = None
    for a in (s1, N - s1):
        for b in (s2, N - s2):
            if a == b: continue
            kk = (z1 - z2) * pow(a - b, -1, N) % N
            d = (a * kk - z1) * pow(r1, -1, N) % N
            if point_mul(G, d) == Q: found = d
    assert found == D
    assert sign_rfc6979(D, z1)[0] != sign_rfc6979(D, z2)[0]     # RFC6979면 r이 다르다


def test_coincurve_cross_check():
    coincurve = pytest.importorskip("coincurve")
    sk = coincurve.PrivateKey(D.to_bytes(32, "big"))
    msg32 = Z.to_bytes(32, "big")
    lib_sig = sk.sign(msg32, hasher=None)                       # libsecp256k1: RFC6979 + low-S, DER
    assert lib_sig == der(*sign_rfc6979(D, Z))                   # 같은 논스 규칙 → 같은 바이트
    r, s = parse_der(lib_sig)
    assert verify(Q, Z, r, s)                                    # 라이브러리 서명 → 내 verify
    mine = der(*sign(D, Z))                                      # 내 서명(무작위 k) → 라이브러리 검증
    assert coincurve.PublicKey(ser_compressed(Q)).verify(mine, msg32, hasher=None)
