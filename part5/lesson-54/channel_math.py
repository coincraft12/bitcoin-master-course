"""13-2 실습 숫자 맞춰 보기 (s132-lab1, s132-lab2). 노드 없이 실행한다.

슬라이드의 LND 0.21.4 실행 결과(정수 sat)를 넣고 잔액이 어디로 갔는지 계산한다.
자기 실행 결과로 바꿔 넣으려면 인자를 준다:

    python part5/lesson-54/channel_math.py
    python part5/lesson-54/channel_math.py --local 996530 --paid 25000 --close-local 970175
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import argparse
import lib  # noqa: F401  (stdout을 UTF-8로 맞춘다: lib/__init__.py)

ANCHOR = 330          # 앵커 출력 하나 (8-4)


def breakdown(capacity: int, local_open: int, paid: int, close_local: int) -> dict:
    reserve = capacity - local_open                  # 개설 직후 local에서 빠진 몫
    commit_fee = reserve - 2 * ANCHOR                # 커밋 트랜잭션 수수료
    local_after = local_open - paid                  # 결제 후 alice 잔액
    close_out = paid + close_local                   # 협력 종료 트랜잭션 출력 합
    close_fee = capacity - close_out                 # 협력 종료 트랜잭션의 실제 수수료
    return {
        "capacity": capacity, "local_open": local_open, "reserve": reserve, "commit_fee": commit_fee,
        "local_after": local_after, "remote_after": paid, "close_out": close_out, "close_fee": close_fee,
        "local_minus_close": local_after - close_local,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", type=int, default=1_000_000)
    ap.add_argument("--local", type=int, default=996_530, help="개설 직후 local_balance")
    ap.add_argument("--paid", type=int, default=25_000, help="bob에게 결제한 금액")
    ap.add_argument("--close-local", type=int, default=970_175, help="협력 종료 후 alice 출력")
    a = ap.parse_args()
    b = breakdown(a.capacity, a.local, a.paid, a.close_local)
    print(f"채널 용량                   {b['capacity']:>11,} sat  (펀딩 출력, P2WSH 2-of-2)")
    print(f"개설 직후 local_balance     {b['local_open']:>11,} sat")
    print(f"  차이                      {b['reserve']:>11,} sat  = 커밋 수수료 {b['commit_fee']:,} + 앵커 {ANCHOR} × 2")
    print(f"결제 후 local / remote      {b['local_after']:>11,} / {b['remote_after']:,} sat  (블록 0개)")
    print(f"협력 종료 출력 합           {b['close_out']:>11,} sat  = {a.paid:,} + {a.close_local:,}")
    print(f"협력 종료 실제 수수료       {b['close_fee']:>11,} sat  = 용량 − 출력 합")
    print(f"local_balance − 종료 출력   {b['local_minus_close']:>11,} sat  = 실제 수수료 {b['close_fee']:,} − 커밋 몫 {b['reserve']:,}")
    print("→ 협력 종료에는 커밋 수수료 예약분과 앵커가 없으므로 그 몫이 개설자(alice)에게 돌아오고,")
    print("  종료 수수료는 개설자가 낸다. 그래서 local_balance와 종료 출력의 차이는 실제 수수료보다 작다.")


if __name__ == "__main__":
    main()
