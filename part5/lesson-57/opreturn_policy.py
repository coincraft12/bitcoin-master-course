"""14-1 실습 보조: OP_RETURN 데이터 크기와 -datacarriersize 정책 판정 (s141-v30, s141-lab). 노드 없이 실행한다.

데이터 N바이트를 담는 nulldata 출력 스크립트 = OP_RETURN(1) + 푸시 접두(1~3) + N.
Core는 트랜잭션 안 모든 OP_RETURN 출력 스크립트 크기의 합이 -datacarriersize 이하일 때만 중계한다
(v30부터 기본 100,000, 여러 개 허용·합산 적용. -datacarriersize=83이면 이전 한도 = 데이터 80바이트).
합의 규칙은 그대로다 — 이것은 내 노드가 무엇을 중계하느냐(정책)의 문제다.

    python part5/lesson-57/opreturn_policy.py                # 슬라이드 표의 크기 31, 80, 81, 99000
    python part5/lesson-57/opreturn_policy.py 75 76 77 255 256
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

OP_RETURN, OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4 = 0x6A, 0x4C, 0x4D, 0x4E
DEFAULT_V30 = 100_000      # Core v30 이후 기본값
LEGACY = 83                # 이전 한도 (데이터 약 80바이트)


def push(data: bytes) -> bytes:
    """최소 푸시 인코딩 (데이터 1바이트 이상)."""
    n = len(data)
    if n <= 75:
        return bytes([n]) + data
    if n <= 0xFF:
        return bytes([OP_PUSHDATA1, n]) + data
    if n <= 0xFFFF:
        return bytes([OP_PUSHDATA2]) + n.to_bytes(2, "little") + data
    return bytes([OP_PUSHDATA4]) + n.to_bytes(4, "little") + data


def nulldata_script(data: bytes) -> bytes:
    return bytes([OP_RETURN]) + push(data)


def relayed(scripts: list, datacarriersize: int) -> bool:
    """정책 판정: OP_RETURN 출력 스크립트 크기 합 ≤ datacarriersize."""
    return sum(len(s) for s in scripts) <= datacarriersize


def main():
    sizes = [int(x) for x in sys.argv[1:]] or [31, 80, 81, 99_000]
    print(f"{'데이터':>10} {'스크립트':>10}   {'기본 설정 (100,000)':<20} -datacarriersize=83")
    for n in sizes:
        data = b"CoinCraft Bitcoin Master Course" if n == 31 else bytes([0xAB]) * n
        s = nulldata_script(data)
        a = "허용" if relayed([s], DEFAULT_V30) else "거부 · datacarrier"
        b = "허용" if relayed([s], LEGACY) else "거부 · datacarrier"
        print(f"{n:>8,}B {len(s):>8,}B   {a:<20} {b}")
    two = [nulldata_script(bytes(40)), nulldata_script(bytes(40))]
    print(f"40바이트 OP_RETURN 2개: 스크립트 합 {sum(map(len, two))}B → 기본 {'허용' if relayed(two, DEFAULT_V30) else '거부'}, "
          f"83 설정 {'허용' if relayed(two, LEGACY) else '거부'} (합산 적용)")


if __name__ == "__main__":
    main()
