"""13-3 실습: 공시된 보유 주소의 잔액 합계를 내 노드로 직접 확인 (s133-questions).

슬라이드 명령을 파이썬으로 감싼 것이다.
    bitcoin-cli scantxoutset start '["addr(<공시된 보유 주소 1>)", "addr(<주소 2>)"]' | jq .total_amount

    python part5/lesson-55/reserve_check.py 주소목록.txt --disclosed 1234.5          # 메인넷 노드
    python part5/lesson-55/reserve_check.py 주소목록.txt --dry-run                    # 노드 없이: 주소 검사, 명령만 출력
    python part5/lesson-55/reserve_check.py 주소목록.txt --network regtest            # regtest로 연습

주소 목록은 한 줄에 주소 하나(# 뒤는 주석). 공시 수치는 BTC 문자열로 받는다(float 금지).
scantxoutset은 현재 UTXO 집합 전체를 훑으므로 메인넷에서는 몇 분 걸릴 수 있다.
14-4 실습(공개 보유 주소를 공시와 비교)에서도 그대로 쓴다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import argparse
import json
from decimal import Decimal
from lib.keys import address_to_script_pubkey
from lib.rpc import RPC, btc_to_sat, sat_to_btc


PREFIXES = {"main": ("bc1", "1", "3"), "regtest": ("bcrt1", "m", "n", "2"),
            "signet": ("tb1", "m", "n", "2"), "testnet4": ("tb1", "m", "n", "2")}


def read_addresses(path: str, network: str = "main") -> list:
    """파일에서 주소를 읽고 형식과 네트워크를 검사한다. 잘못된 주소는 ValueError (줄 번호 포함)."""
    out = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        a = line.split("#", 1)[0].strip()
        if not a:
            continue
        try:
            address_to_script_pubkey(a)
        except ValueError as e:
            raise ValueError(f"{path}:{n} 주소 형식 오류 {a!r}: {e}") from None
        pre = PREFIXES[network]
        if not a.lower().startswith(pre) or (network != "regtest" and a.lower().startswith("bcrt1")):
            raise ValueError(f"{path}:{n} {a!r}는 {network} 주소가 아닙니다 (기대 접두어 {', '.join(pre)})")
        out.append(a)
    if not out:
        raise ValueError("주소가 하나도 없습니다")
    return out


def scan_objects(addrs: list) -> list:
    return [f"addr({a})" for a in addrs]


def compare(total_sat: int, disclosed_sat: int) -> str:
    diff = total_sat - disclosed_sat
    sign = "+" if diff >= 0 else "−"
    if disclosed_sat:
        bp = abs(diff) * 10000 // disclosed_sat           # 만분율 (float 없이)
        return f"차이 {sign}{sat_to_btc(abs(diff)):f} BTC ({sign}{bp // 100}.{bp % 100:02d}%)"
    return f"차이 {sign}{sat_to_btc(abs(diff)):f} BTC"


def main():
    ap = argparse.ArgumentParser(description="공시 보유 주소 잔액 합계 확인")
    ap.add_argument("address_file")
    ap.add_argument("--disclosed", help="공시된 보유량 (BTC, 예: 1234.5)")
    ap.add_argument("--network", default="main")
    ap.add_argument("--dry-run", action="store_true", help="노드에 묻지 않고 주소 검사와 명령만")
    a = ap.parse_args()

    try:
        addrs = read_addresses(a.address_file, a.network)
    except ValueError as e:
        sys.exit(str(e))
    objs = scan_objects(addrs)
    print(f"주소 {len(addrs)}개 형식 확인 완료")
    if a.dry_run:
        net = "" if a.network == "main" else f" -{a.network}"
        print(f"bitcoin-cli{net} scantxoutset start '{json.dumps(objs)}' | jq .total_amount")
        return
    res = RPC(a.network).scantxoutset("start", objs)
    total = btc_to_sat(str(res["total_amount"]))
    print(f"UTXO {len(res['unspents'])}개, 높이 {res.get('height')}")
    print(f"내 노드가 센 잔액 합계: {sat_to_btc(total):f} BTC")
    if a.disclosed:
        disclosed = btc_to_sat(Decimal(a.disclosed))
        print(f"공시 수치            : {sat_to_btc(disclosed):f} BTC")
        print(compare(total, disclosed))
    print("→ \"이 BTC를 누가, 어떤 조건으로 풀 수 있나\"(키 보유 주체·정족수·검증 소프트웨어)와 함께 한 단락으로 정리한다.")


if __name__ == "__main__":
    main()
