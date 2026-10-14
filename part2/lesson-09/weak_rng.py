"""3-1 보충: 약한 난수(s31-fail)로 만든 키가 왜 위험한가.

시각을 시드로 쓰는 random 모듈로 키를 만들면, 공격자는 그 시각 근처의 시드만 다시 돌려 보면
같은 키를 재현한다. 교육용 시연이며 실제 키 생성에는 secrets(CSPRNG)만 쓴다.
실행: python part2/lesson-09/weak_rng.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import random
import time
from lib.ec import N
from lib.keys import public_key


def weak_key(seed: int) -> int:
    rng = random.Random(seed)               # 나쁜 예: 예측 가능한 시드
    return rng.randrange(1, N)


victim_seed = int(time.time()) - random.randrange(0, 600)   # 최근 10분 안의 어느 초
victim_pub = public_key(weak_key(victim_seed))
print("피해자 공개키 x:", hex(victim_pub[0]))

now = int(time.time())
start = time.perf_counter()
for guess in range(now, now - 3600, -1):    # 공격자: 최근 1시간을 1초 단위로 시도
    if public_key(weak_key(guess)) == victim_pub:
        print(f"찾음: 시드 {guess}, 시도 {now - guess + 1}번, {time.perf_counter() - start:.1f}초")
        break
print("키 공간은 2^256이어도 실제 후보는 수천 개뿐이었다.")
