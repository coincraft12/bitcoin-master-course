"""교육용 구현. 실제 자금에 쓰지 말 것.

secp256k1 타원곡선 연산 (3-1). 3부까지 계속 쓰는 기반 코드이므로
함수 이름과 인자 순서를 고정한다: point_mul(점, 스칼라).

    from lib.ec import FIELD_P, N, G, is_on_curve, point_add, point_mul

점은 (x, y) 정수 튜플, 무한원점은 None.
"""
# 교육용 구현: 상수 시간 연산이 아니므로 실제 자금의 키에 쓰지 말 것
FIELD_P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


def is_on_curve(P) -> bool:
    if P is None:
        return True                      # None = 무한원점
    x, y = P
    return (y * y - x * x * x - 7) % FIELD_P == 0


def point_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % FIELD_P == 0:
        return None                          # P + (−P)
    if P == Q:                               # 접선
        lam = 3 * P[0] * P[0] * pow(2 * P[1], -1, FIELD_P) % FIELD_P
    else:                                    # 두 점을 잇는 직선
        lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, FIELD_P) % FIELD_P
    x = (lam * lam - P[0] - Q[0]) % FIELD_P
    y = (lam * (P[0] - x) - P[1]) % FIELD_P
    return (x, y)


# double-and-add
def point_mul(P, k: int):
    R = None
    while k:
        if k & 1:
            R = point_add(R, P)
        P = point_add(P, P)
        k >>= 1
    return R
