"""11-5 BIP9 상태 전이 시뮬레이션 (노드 없이 실행).

regtest 시험용 배포 testdummy (Core 31 chainparams: bit 28, 구간 144, 임계치 108, 시작 시각 0, 만료 없음)를
Core의 규칙대로 따라가며, testdummy_lab.sh가 144블록씩 세 번 만들 때 getdeploymentinfo가 보여 줄
status·since와 블록 헤더 version을 계산한다.
- 상태는 구간(144블록) 경계에서만 바뀐다. 한 구간의 상태는 직전 구간의 신호 수로 정해진다.
- Core의 블록 템플릿은 STARTED·LOCKED_IN 구간에 bit 28을 켠다(채굴자가 모두 Core라고 가정).

    python part4/lesson-48/bip9_sim.py
    python part4/lesson-48/bip9_sim.py 102     # setup_regtest.sh 뒤처럼 높이 102에서 시작할 때
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.block import signals_bit, VERSIONBITS_TOP_BITS

BIT, PERIOD, THRESHOLD = 28, 144, 108


def simulate(tip: int, signal=lambda h, state: state in ("started", "locked_in")):
    """높이 0..tip 각 블록의 (상태, version). 상태는 그 블록에 적용되는 상태."""
    states, versions = [], []
    state = "defined"
    for h in range(tip + 1):
        if h > 0 and h % PERIOD == 0:                      # 구간 경계에서 전이
            if state == "defined":
                state = "started"                           # 시작 시각 0 (h=0 구간은 항상 defined)
            elif state == "started":
                count = sum(signals_bit(versions[k], BIT) for k in range(h - PERIOD, h))
                if count >= THRESHOLD:
                    state = "locked_in"
            elif state == "locked_in":
                state = "active"
        states.append(state)
        v = 1 if h == 0 else VERSIONBITS_TOP_BITS | (1 << BIT if signal(h, state) else 0)   # 제네시스 version 1
        versions.append(v)
    return states, versions


def since(states, tip):
    h = tip
    while h > 0 and states[h - 1] == states[tip]:
        h -= 1
    return h


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    tips = [start + 144 * i for i in (1, 2, 3)]
    states, versions = simulate(tips[-1])
    print("tip  status     since")
    for t in tips:
        print(f"{t:>3}  {states[t]:<10} {since(states, t)}")
    print("높이별 헤더 version:")
    for h in (143, 144, 287, 288, 431, 432):
        if h <= tips[-1]:
            print(f"  {h:>3}: {versions[h]:#010x}  bit28={signals_bit(versions[h], BIT)}")
    print("신호가 임계치에 못 미치면 (구간당 107블록만 신호):")
    st, _ = simulate(432, signal=lambda h, s: s in ("started", "locked_in") and h % PERIOD < 107)
    print(f"  432: {st[432]}  (만료 시각이 없어 started에 머문다)")
