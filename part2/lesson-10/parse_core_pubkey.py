"""3-2 실습: Core가 준 공개키(hex)를 곡선 위의 점으로 복원.

    PUB=$(bitcoin-cli -regtest -rpcwallet=alice getaddressinfo \
          $(bitcoin-cli -regtest -rpcwallet=alice getnewaddress "" legacy) | jq -r .pubkey)
    python part2/lesson-10/parse_core_pubkey.py $PUB
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import is_on_curve
from lib.keys import parse_pubkey, ser_uncompressed

if len(sys.argv) != 2:
    sys.exit("사용법: python part2/lesson-10/parse_core_pubkey.py <공개키 hex>")
b = bytes.fromhex(sys.argv[1])
Q = parse_pubkey(b)
print("입력 길이   :", len(b), "바이트, 접두사", b[:1].hex())
print("x           :", hex(Q[0]))
print("y (복원)    :", hex(Q[1]), "(짝수)" if Q[1] % 2 == 0 else "(홀수)")
print("곡선 위     :", is_on_curve(Q))
print("비압축 형식 :", ser_uncompressed(Q).hex())
