"""8-4 패키지 수수료율 = 합계 수수료 ÷ 합계 크기 (s84-idea, s84-quiz, s84-lab2).

    python part4/lesson-35/package_feerate.py                    # 슬라이드 예제 (노드 없이)
    python part4/lesson-35/package_feerate.py --mempool P C      # 멤풀의 부모·자식 txid로 계산 (regtest 노드)

금액은 sat 정수. 수수료율은 소수 둘째 자리까지 표시한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from decimal import Decimal


def rate(fee: int, vsize: int) -> Decimal:
    return (Decimal(fee) / vsize).quantize(Decimal("0.01"))


def package_rate(items: list[tuple]) -> Decimal:
    """items = [(수수료 sat, vsize vB), ...] → 크기로 가중한 수수료율."""
    return rate(sum(f for f, _ in items), sum(v for _, v in items))


def show(name: str, items: list[tuple]):
    parts = " + ".join(f"{f} sat/{v} vB({rate(f, v)})" for f, v in items)
    print(f"{name}: {parts} → 패키지 {sum(f for f, _ in items)} ÷ {sum(v for _, v in items)}"
          f" = {package_rate(items)} sat/vB")


def from_mempool(txids: list[str]):
    from lib.rpc import RPC, btc_to_sat
    rpc = RPC()
    items = []
    for t in txids:
        e = rpc.getmempoolentry(t)
        fee = btc_to_sat(e["fees"]["base"])
        items.append((fee, e["vsize"]))
        extra = {k: str(v) for k, v in e["fees"].items() if k != "base"}
        print(f"{t[:16]}… vsize {e['vsize']} vB, base {fee} sat ({rate(fee, e['vsize'])} sat/vB), 그 밖의 fees {extra}")
    show("손 계산", items)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--mempool":
        from_mempool(sys.argv[2:])
        sys.exit(0)
    show("s84-idea", [(200, 200), (2800, 100)])
    print("  틀린 계산: 두 수수료율의 단순 평균 =", (Decimal(1) + Decimal(28)) / 2, "sat/vB (크기로 가중해야 한다)")
    # s84-lab2: 부모 141 vB·141 sat(1 sat/vB), 자식은 0.2 BTC 입력 → 0.1997 BTC 출력(수수료 30,000 sat).
    # 자식 크기 110 vB는 P2WPKH 입력 1·출력 1의 vsize(10.5 + 68 + 31 = 109.5 → 110)
    show("s84-lab2", [(141, 141), (20_000_000 - 19_970_000, 110)])
    print("  부모 단독 1.00 sat/vB < 문턱 5 sat/vB → testmempoolaccept 거부, 패키지는 약 120 sat/vB로 수락")
