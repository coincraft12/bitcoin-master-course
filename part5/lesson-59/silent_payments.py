"""14-3 실습: Silent Payments 원리 계산 — 교육용 단순화 (s143-lab).

실제 BIP352는 입력 정보 해시(input_hash), 여러 출력 번호 k, 레이블을 포함하고, 공유 비밀은
33바이트 압축 형식으로 해시한다. 여기서는 슬라이드대로 입력 하나·출력 하나, x좌표 32바이트로
원리만 본다. 실제 구현은 BIP352 참조 구현과 테스트 벡터로 검증해야 한다.

    python part5/lesson-59/silent_payments.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, N, point_add, point_mul
from lib.keys import new_private_key
from lib.hashes import tagged_hash

# ---- 슬라이드 코드 (s143-lab) ----
b_scan, b_spend = new_private_key(), new_private_key()            # 받는 사람
B_scan, B_spend = point_mul(G, b_scan), point_mul(G, b_spend)
a = new_private_key(); A = point_mul(G, a)                          # 보내는 사람
S_send = point_mul(B_scan, a)
t = int.from_bytes(tagged_hash("BIP0352/SharedSecret",
        S_send[0].to_bytes(32, "big") + (0).to_bytes(4, "big")), "big") % N
P_out = point_add(B_spend, point_mul(G, t))
S_recv = point_mul(A, b_scan)                                       # 받는 사람
t2 = int.from_bytes(tagged_hash("BIP0352/SharedSecret",
        S_recv[0].to_bytes(32, "big") + (0).to_bytes(4, "big")), "big") % N
print(point_add(B_spend, point_mul(G, t2)) == P_out)    # True
print(point_mul(G, (b_spend + t2) % N) == P_out)         # True: 받는 사람만 쓸 수 있다


# ---- (저장소 보충) 같은 받는 사람에게 다른 a로 한 번 더 보내면 출력이 달라진다 ----
def sp_output(a_priv: int) -> tuple:
    """보내는 사람의 입력 개인키 a로 만든 출력 키 P (슬라이드와 같은 단순화)."""
    S = point_mul(B_scan, a_priv)
    tk = int.from_bytes(tagged_hash("BIP0352/SharedSecret",
            S[0].to_bytes(32, "big") + (0).to_bytes(4, "big")), "big") % N
    return point_add(B_spend, point_mul(G, tk))


P_out2 = sp_output(new_private_key())
print("다른 a로 보낸 두 출력이 다르다:", P_out2 != P_out)
print("두 출력의 x좌표 앞 8바이트:", P_out[0].to_bytes(32, "big")[:8].hex(), P_out2[0].to_bytes(32, "big")[:8].hex())
