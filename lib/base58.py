"""교육용 구현. 실제 자금에 쓰지 말 것.

Base58 / Base58Check 인코딩 (3-3). 레거시 주소(1…, 3…, m/n…, 2…), WIF,
확장 키(xprv/xpub/tprv/tpub)가 이 형식을 쓴다.

    from lib.base58 import b58encode, b58decode, b58check_encode, b58check_decode
"""
from lib.hashes import dsha256

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(b: bytes) -> str:
    n, s = int.from_bytes(b, "big"), ""
    while n:
        n, r = divmod(n, 58)
        s = ALPHABET[r] + s
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + s


def b58decode(s: str) -> bytes:
    n = 0
    for c in s:
        i = ALPHABET.find(c)
        if i < 0:
            raise ValueError(f"Base58에 없는 문자: {c!r}")
        n = n * 58 + i
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\x00" * (len(s) - len(s.lstrip("1"))) + body   # 앞쪽 '1'은 0x00 바이트


def b58check_encode(payload: bytes) -> str:
    return b58encode(payload + dsha256(payload)[:4])


def b58check_decode(s: str) -> bytes:
    raw = b58decode(s)
    if len(raw) < 4: raise ValueError("너무 짧음")
    payload, check = raw[:-4], raw[-4:]
    if dsha256(payload)[:4] != check: raise ValueError("체크섬 불일치")
    return payload
