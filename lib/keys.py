"""교육용 구현. 실제 자금에 쓰지 말 것.

키 생성, 공개키 직렬화·파싱, WIF, 주소 (3-1 ~ 3-5).

    from lib.keys import new_private_key, public_key, ser_compressed, p2wpkh_address

버전 바이트와 HRP (3-3, 3-4)
    P2PKH  mainnet 0x00 (1…)    testnet·regtest 0x6f (m/n…)
    P2SH   mainnet 0x05 (3…)    testnet·regtest 0xc4 (2…)
    WIF    mainnet 0x80 (K/L/5) testnet·regtest 0xef (c/9)
    HRP    bc (mainnet) · tb (testnet·signet) · bcrt (regtest)

P2TR 주소의 출력키 계산(내부키 조정)은 6-4의 lib/taproot.py(output_key) 몫이다.
여기 p2tr_address는 이미 조정된 32바이트 출력키를 bech32m으로 적기만 한다.
"""
import secrets

from lib.ec import FIELD_P, N, G, is_on_curve, point_mul
from lib.hashes import sha256, hash160
from lib.base58 import b58check_encode, b58check_decode
from lib import segwit_addr


# ── 3-1 키 생성 ─────────────────────────────────────────────
def new_private_key() -> int:
    return secrets.randbelow(N - 1) + 1


def public_key(d: int):
    return point_mul(G, d)


# ── 3-2 공개키 형식 ─────────────────────────────────────────
def ser_uncompressed(Q) -> bytes:
    return b"\x04" + Q[0].to_bytes(32, "big") + Q[1].to_bytes(32, "big")


def ser_compressed(Q) -> bytes:
    return (b"\x03" if Q[1] % 2 else b"\x02") + Q[0].to_bytes(32, "big")


def ser_xonly(Q) -> bytes:
    return Q[0].to_bytes(32, "big")


def parse_pubkey(b: bytes):
    if b[0] == 0x04 and len(b) == 65:
        Q = (int.from_bytes(b[1:33], "big"), int.from_bytes(b[33:], "big"))
    elif b[0] in (0x02, 0x03) and len(b) == 33:
        x = int.from_bytes(b[1:], "big")
        if x >= FIELD_P: raise ValueError("x 범위 초과")
        y = pow((pow(x, 3, FIELD_P) + 7) % FIELD_P, (FIELD_P + 1) // 4, FIELD_P)
        if y % 2 != b[0] - 2: y = FIELD_P - y
        Q = (x, y)
    else:
        raise ValueError("알 수 없는 형식")
    if not is_on_curve(Q): raise ValueError("곡선 위의 점이 아님")
    return Q


def parse_xonly(b: bytes):
    """32바이트 x-only 공개키 → 짝수 y 점 (BIP340 약속)."""
    if len(b) != 32: raise ValueError("x-only 키는 32바이트")
    return parse_pubkey(b"\x02" + b)


# ── 3-3 레거시 주소와 WIF ───────────────────────────────────
def p2pkh_address(pubkey: bytes, version: int = 0x00) -> str:
    return b58check_encode(bytes([version]) + hash160(pubkey))


def p2sh_address(redeem_script: bytes, version: int = 0x05) -> str:
    return b58check_encode(bytes([version]) + hash160(redeem_script))


def wif(d: int, compressed: bool = True, version: int = 0x80) -> str:
    return b58check_encode(bytes([version]) + d.to_bytes(32, "big") + (b"\x01" if compressed else b""))


def parse_wif(s: str):
    """WIF → (개인키 정수, 압축 여부, 버전 바이트)."""
    raw = b58check_decode(s)
    if len(raw) == 34 and raw[-1] == 0x01:
        compressed = True
    elif len(raw) == 33:
        compressed = False
    else:
        raise ValueError("WIF 길이 오류")
    d = int.from_bytes(raw[1:33], "big")
    if not 1 <= d < N: raise ValueError("개인키 범위 오류")
    return d, compressed, raw[0]


# ── 3-4 SegWit v0 주소 ──────────────────────────────────────
def p2wpkh_address(pubkey_compressed: bytes, hrp: str = "bc") -> str:
    return segwit_addr.encode(hrp, 0, hash160(pubkey_compressed))


def p2wsh_address(witness_script: bytes, hrp: str = "bc") -> str:
    return segwit_addr.encode(hrp, 0, sha256(witness_script))


def p2sh_p2wpkh_address(pubkey_compressed: bytes, version: int = 0x05) -> str:
    return p2sh_address(b"\x00\x14" + hash160(pubkey_compressed), version)


# ── 3-5 Taproot 주소 (출력키 계산은 6-4 lib/taproot.py) ─────
def p2tr_address(output_xonly: bytes, hrp: str = "bc") -> str:
    """조정이 끝난 32바이트 출력키 → bc1p 주소 (bech32m, witness v1)."""
    if len(output_xonly) != 32: raise ValueError("출력키는 32바이트 x-only")
    return segwit_addr.encode(hrp, 1, output_xonly)


# ── 주소 → 잠금 스크립트(scriptPubKey) ─────────────────────
P2PKH_VERSIONS = (0x00, 0x6f)
P2SH_VERSIONS = (0x05, 0xc4)
HRPS = ("bc", "tb", "bcrt")


def address_to_script_pubkey(addr: str) -> bytes:
    """주소를 잠금 스크립트 바이트로. 형식이 틀리면 ValueError."""
    for hrp in HRPS:
        if addr.lower().startswith(hrp + "1"):
            ver, prog = segwit_addr.decode(hrp, addr)
            if ver is None:
                raise ValueError("잘못된 bech32/bech32m 주소")
            return bytes([ver + 0x50 if ver else 0, len(prog)]) + bytes(prog)
    payload = b58check_decode(addr)
    if len(payload) != 21:
        raise ValueError("레거시 주소 길이 오류")
    if payload[0] in P2PKH_VERSIONS:
        return b"\x76\xa9\x14" + payload[1:] + b"\x88\xac"   # OP_DUP OP_HASH160 <20> OP_EQUALVERIFY OP_CHECKSIG
    if payload[0] in P2SH_VERSIONS:
        return b"\xa9\x14" + payload[1:] + b"\x87"           # OP_HASH160 <20> OP_EQUAL
    raise ValueError(f"알 수 없는 버전 바이트 {payload[0]:#04x}")
