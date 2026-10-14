"""3-1 실습 마지막 단계: 같은 개인키의 공개키를 검증용 라이브러리 coincurve와 대조.

coincurve는 libsecp256k1 바인딩이다. lib은 표준 라이브러리만 쓰므로 이 대조용으로만 설치한다.
    pip install coincurve
실행: python part2/lesson-09/compare_coincurve.py [개인키16진수]
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.keys import new_private_key, public_key

try:
    import coincurve
except ImportError:
    print("coincurve가 없습니다. 대조하려면: pip install coincurve")
    sys.exit(0)

d = int(sys.argv[1], 16) if len(sys.argv) > 1 else new_private_key()
mine = public_key(d)
ref = coincurve.PrivateKey(d.to_bytes(32, "big")).public_key.format(compressed=False)
theirs = (int.from_bytes(ref[1:33], "big"), int.from_bytes(ref[33:], "big"))
print("d          :", hex(d))
print("lib x      :", hex(mine[0]))
print("coincurve x:", hex(theirs[0]))
print("lib y      :", hex(mine[1]))
print("coincurve y:", hex(theirs[1]))
print("일치       :", mine == theirs)
