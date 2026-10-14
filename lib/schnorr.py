"""교육용 구현. 실제 자금에 쓰지 말 것.

BIP340 Schnorr 서명 (7-3 s73-code1·2 슬라이드 그대로 + 공개키 보조 함수).

    from lib.schnorr import sign, verify, pubkey_gen
    sig = sign(msg, seckey32, aux_rand32)        # 64바이트 = R.x ‖ s
    verify(msg, xonly_pubkey32, sig)              # True / False

msg는 임의 길이 바이트(Taproot에서는 32바이트 서명 해시, 7-4). 공식 벡터: data/bip340_test_vectors.csv
상수 시간 연산이 아니므로 부채널 공격에 취약하다.
"""
from lib.ec import G, N, FIELD_P, point_add, point_mul
from lib.taproot import tagged_hash, lift_x   # lift_x에 x ≥ FIELD_P 검사 한 줄 추가


def b32(x): return x.to_bytes(32, "big")
def to_int(b): return int.from_bytes(b, "big")
def even_y(P): return P[1] % 2 == 0
def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))


def sign(msg: bytes, seckey: bytes, aux_rand: bytes) -> bytes:
    d0 = to_int(seckey); assert 1 <= d0 < N
    P = point_mul(G, d0)
    d = d0 if even_y(P) else N - d0
    t = xor(b32(d), tagged_hash("BIP0340/aux", aux_rand))
    k0 = to_int(tagged_hash("BIP0340/nonce", t + b32(P[0]) + msg)) % N
    assert k0 != 0
    R = point_mul(G, k0)
    k = k0 if even_y(R) else N - k0
    e = to_int(tagged_hash("BIP0340/challenge", b32(R[0]) + b32(P[0]) + msg)) % N
    return b32(R[0]) + b32((k + e * d) % N)


def verify(msg: bytes, pubkey: bytes, sig: bytes) -> bool:
    if len(pubkey) != 32 or len(sig) != 64: return False
    try: P = lift_x(to_int(pubkey))
    except ValueError: return False
    r, s = to_int(sig[:32]), to_int(sig[32:])
    if r >= FIELD_P or s >= N: return False
    e = to_int(tagged_hash("BIP0340/challenge", sig[:32] + pubkey + msg)) % N
    R = point_add(point_mul(G, s), point_mul(P, N - e))
    return R is not None and even_y(R) and R[0] == r


def pubkey_gen(seckey: bytes) -> bytes:
    """BIP340 x-only 공개키 32B (P = d·G의 x좌표)."""
    d0 = to_int(seckey)
    if not 1 <= d0 < N: raise ValueError("개인키 범위 밖")
    return b32(point_mul(G, d0)[0])
