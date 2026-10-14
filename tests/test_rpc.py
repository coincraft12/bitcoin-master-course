"""lib/rpc.py — 노드 없이 쿠키 읽기·금액 변환·응답 처리를 확인한다(requests.post를 가짜로 바꾼다)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from decimal import Decimal
import json
import pytest
import lib.rpc as rpcmod
from lib.rpc import RPC, btc_to_sat, sat_to_btc


def make_datadir(tmp_path, network="regtest", cookie="__cookie__:secret"):
    d = tmp_path / network
    d.mkdir()
    (d / ".cookie").write_text(cookie, encoding="utf-8")
    return str(tmp_path)


class FakeResp:
    def __init__(self, text):
        self.text = text
    def json(self, parse_float=float):
        return json.loads(self.text, parse_float=parse_float)
    def raise_for_status(self):
        raise RuntimeError("http error")


def test_missing_cookie_message(tmp_path):
    with pytest.raises(RuntimeError, match="쿠키 파일이 없습니다"):
        RPC(datadir=str(tmp_path))


def test_cookie_url_and_call(tmp_path, monkeypatch):
    seen = {}
    def fake_post(url, auth, json):
        seen.update(url=url, auth=auth, body=json)
        return FakeResp('{"result": {"amount": 0.00000001}, "error": null, "id": "cc"}')
    monkeypatch.setattr(rpcmod.requests, "post", fake_post)
    r = RPC(datadir=make_datadir(tmp_path), wallet="alice")
    out = r.getbalances(1, "x")
    assert seen["url"] == "http://127.0.0.1:18443/wallet/alice"
    assert seen["auth"] == ("__cookie__", "secret")
    assert seen["body"]["method"] == "getbalances" and seen["body"]["params"] == [1, "x"]
    assert isinstance(out["amount"], Decimal) and out["amount"] == Decimal("0.00000001")   # float를 거치지 않는다


def test_error_response_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(rpcmod.requests, "post",
                        lambda url, auth, json: FakeResp('{"result": null, "error": {"code": -5, "message": "no"}, "id": "cc"}'))
    with pytest.raises(RuntimeError, match="getblock"):
        RPC(datadir=make_datadir(tmp_path)).getblock("00")


def test_network_ports_and_subdir(tmp_path):
    r = RPC(network="signet", datadir=make_datadir(tmp_path, "signet"))
    assert r.url == "http://127.0.0.1:38332/"
    m = tmp_path / "m"; m.mkdir(); (m / ".cookie").write_text("u:p", encoding="utf-8")
    assert RPC(network="main", datadir=str(m)).url == "http://127.0.0.1:8332/"       # main은 하위 폴더 없음


def test_btc_sat_conversion():
    assert btc_to_sat(Decimal("0.00000001")) == 1
    assert btc_to_sat("1.5") == 150_000_000
    assert sat_to_btc(123_456_789) == Decimal("1.23456789")
    assert sat_to_btc(1) == Decimal("0.00000001")
    with pytest.raises(TypeError):
        btc_to_sat(0.1)
