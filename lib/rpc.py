"""Bitcoin Core JSON-RPC 래퍼 (2-4).

    from lib.rpc import RPC
    rpc = RPC()                    # regtest, 노드 RPC
    alice = RPC(wallet="alice")    # /wallet/alice 지갑 RPC
    rpc.getblock(rpc.getblockhash(0), 1)

금액은 Decimal로 받는다. 내부 계산은 sat 정수로 한다.
"""
import os
import requests
from decimal import Decimal

PORTS = {"main": 8332, "testnet4": 48332, "signet": 38332, "regtest": 18443}

DEFAULT_DATADIR = os.environ.get("BITCOIN_DATADIR", os.path.expanduser("~/.bitcoin"))


class RPC:
    def __init__(self, network="regtest", wallet=None, datadir=DEFAULT_DATADIR):
        sub = "" if network == "main" else network
        cookie = os.path.join(datadir, sub, ".cookie")
        try:
            user, pw = open(cookie).read().strip().split(":", 1)
        except FileNotFoundError:
            raise RuntimeError(
                f"쿠키 파일이 없습니다: {cookie}\n"
                "노드가 실행 중인지(bitcoind -regtest -daemon), datadir이 맞는지 확인하세요."
            ) from None
        self.auth = (user, pw)
        self.url = f"http://127.0.0.1:{PORTS[network]}/" + (f"wallet/{wallet}" if wallet else "")

    def __getattr__(self, method):
        if method.startswith("__"):
            raise AttributeError(method)

        def call(*params):
            r = requests.post(self.url, auth=self.auth, json={
                "jsonrpc": "1.0", "id": "cc", "method": method, "params": list(params)})
            try:
                body = r.json(parse_float=Decimal)
            except ValueError:
                r.raise_for_status()
                raise
            if body.get("error"):
                raise RuntimeError(f"{method}: {body['error']}")
            return body["result"]

        return call


def btc_to_sat(btc) -> int:
    """Decimal BTC → 정수 sat. float는 받지 않는다."""
    if isinstance(btc, float):
        raise TypeError("금액에 float를 쓰지 마세요. Decimal 또는 str로 넘기세요.")
    return int(Decimal(btc) * 100_000_000)


def sat_to_btc(sat: int) -> Decimal:
    return (Decimal(sat) / Decimal(100_000_000)).quantize(Decimal("0.00000001"))
