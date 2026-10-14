"""9-1 실습: 내 노드의 피어 분석 (s91-lab).

    python part4/lesson-37/my_peers.py            # signet 노드 (슬라이드 그대로)
    python part4/lesson-37/my_peers.py main       # 메인넷 노드
    python part4/lesson-37/my_peers.py regtest    # 노드가 없으면 9-2의 regtest 2노드 환경으로

결과를 연결 유형 표(전체 릴레이 8, 블록 전용 2, 피일러, 인바운드)와 대조한다.
노드를 막 켠 직후에는 피어 수가 적을 수 있으니 잠시 기다렸다가 다시 실행한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from collections import Counter
from lib.rpc import RPC
rpc = RPC(network="signet") if len(sys.argv) < 2 else RPC(network=sys.argv[1])
peers = rpc.getpeerinfo()
print("총 피어:", len(peers))
print("방향:", Counter("inbound" if p["inbound"] else "outbound" for p in peers))
print("연결 유형:", Counter(p["connection_type"] for p in peers))
print("네트워크:", Counter(p["network"] for p in peers))
print("전송 방식:", Counter(p.get("transport_protocol_type") for p in peers))
for p in sorted(peers, key=lambda p: p.get("pingtime", 9))[:5]:
    print(p["addr"], p["subver"], round(p.get("pingtime", 0) * 1000), "ms")

# (저장소 보탬) 주소록 크기: getnodeaddresses 0 = 전부
addrs = rpc.getnodeaddresses(0)
print("주소록 크기:", len(addrs), "· 네트워크별:", Counter(a["network"] for a in addrs))
