"""교육용 구현. 실제 자금에 쓰지 말 것.

ECDSA 서명·검증·DER (7-1 s71-code1·2) + RFC6979 결정적 논스 (7-2 s72-code "이어서").

    from lib.ecdsa import sign, verify, der, parse_der, rfc6979_nonce, sign_rfc6979

- sign(d, z, k=None)    k를 주지 않으면 secrets 난수. k를 열어 둔 것은 7-2 논스 재사용 실험용
- verify(Q, z, r, s)    Q는 점 (x, y). high-S도 수학적으로는 통과한다 (low-S는 정책)
- der(r, s)             sighash 바이트를 붙이기 전의 DER 본문
- parse_der(sig)        DER → (r, s). 끝에 sighash 바이트가 붙어 있으면 떼고 넘길 것
- rfc6979_nonce(d, z)   RFC 6979 3.2절 HMAC-SHA256 결정적 k (libsecp256k1 기본 논스와 같다)
- sign_rfc6979(d, z)    = sign(d, z, rfc6979_nonce(d, z)). 같은 메시지면 같은 서명

z는 메시지 해시(서명 해시)를 빅 엔디안 정수로 읽은 값이다: int.from_bytes(sighash, "big").
상수 시간 연산이 아니므로 부채널 공격에 취약하다.
"""
import hashlib
import hmac
import secrets
from lib.ec import G, N, point_add, point_mul


def sign(d: int, z: int, k: int | None = None) -> tuple[int, int]:
    while True:
        kk = k if k is not None else secrets.randbelow(N - 1) + 1
        R = point_mul(G, kk)
        r = R[0] % N
        s = pow(kk, -1, N) * (z + r * d) % N
        if r and s: break
    if s > N // 2: s = N - s                # low-S
    return r, s


def verify(Q, z: int, r: int, s: int) -> bool:
    if not (1 <= r < N and 1 <= s < N): return False
    w = pow(s, -1, N)
    X = point_add(point_mul(G, z * w % N), point_mul(Q, r * w % N))
    return X is not None and X[0] % N == r


def der(r: int, s: int) -> bytes:
    def enc(x: int) -> bytes:
        b = x.to_bytes(32, "big").lstrip(b"\x00")
        if b[0] & 0x80: b = b"\x00" + b
        return b"\x02" + bytes([len(b)]) + b
    body = enc(r) + enc(s)
    return b"\x30" + bytes([len(body)]) + body


def parse_der(sig: bytes) -> tuple[int, int]:
    """DER 서명 → (r, s). 형식이 어긋나면 ValueError. (BIP66 엄격 규칙 전체가 아니라 구조만 본다)"""
    if len(sig) < 8 or sig[0] != 0x30 or sig[1] != len(sig) - 2:
        raise ValueError("DER 형식이 아님 (sighash 바이트를 떼었는지 확인)")
    i, vals = 2, []
    for _ in range(2):
        if sig[i] != 0x02: raise ValueError("정수 표지 0x02가 없음")
        n = sig[i + 1]
        vals.append(int.from_bytes(sig[i + 2:i + 2 + n], "big"))
        i += 2 + n
    if i != len(sig): raise ValueError("남는 바이트가 있음")
    return vals[0], vals[1]


def rfc6979_nonce(d: int, z: int) -> int:
    """RFC 6979 3.2절: HMAC-DRBG(SHA256)에 개인키 d와 메시지 해시 z(mod n)를 넣어 k를 만든다."""
    x = d.to_bytes(32, "big")
    h = (z % N).to_bytes(32, "big")
    V, K = b"\x01" * 32, b"\x00" * 32
    K = hmac.new(K, V + b"\x00" + x + h, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    K = hmac.new(K, V + b"\x01" + x + h, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    while True:
        V = hmac.new(K, V, hashlib.sha256).digest()
        k = int.from_bytes(V, "big")
        if 1 <= k < N:
            return k
        K = hmac.new(K, V + b"\x00", hashlib.sha256).digest()
        V = hmac.new(K, V, hashlib.sha256).digest()


def sign_rfc6979(d: int, z: int) -> tuple[int, int]:
    return sign(d, z, rfc6979_nonce(d, z))
