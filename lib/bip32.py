"""교육용 구현. 실제 자금에 쓰지 말 것.

BIP32 HD 키 파생 (4-2): 마스터 키, 일반·강화 자식 파생, 경로, 78바이트 직렬화.

    from lib.bip32 import HARD, master, ckd_priv, ckd_pub, derive_priv, serialize, fingerprint

개인키는 정수 k, 공개키는 점 K=(x, y), 체인코드는 32바이트 c.
경로 표기는 h, H, ' 모두 강화 파생으로 읽는다: "m/84h/0'/0H/0/5".
"""
import hashlib
import hmac

from lib.ec import N, G, point_add, point_mul
from lib.hashes import hash160
from lib.base58 import b58check_encode, b58check_decode
from lib.keys import ser_compressed, parse_pubkey

HARD = 0x80000000

# 버전 4바이트 → 접두어 (mainnet xprv·xpub, testnet·regtest tprv·tpub)
VERSIONS = {
    "xprv": bytes.fromhex("0488ade4"), "xpub": bytes.fromhex("0488b21e"),
    "tprv": bytes.fromhex("04358394"), "tpub": bytes.fromhex("043587cf"),
}


def hmac512(key, data): return hmac.new(key, data, hashlib.sha512).digest()


def master(seed: bytes):
    I = hmac512(b"Bitcoin seed", seed)
    return int.from_bytes(I[:32], "big"), I[32:]              # (개인키, 체인코드)


def ckd_priv(k: int, c: bytes, i: int):
    if i >= HARD: data = b"\x00" + k.to_bytes(32, "big") + i.to_bytes(4, "big")
    else:         data = ser_compressed(point_mul(G, k)) + i.to_bytes(4, "big")
    I = hmac512(c, data); il = int.from_bytes(I[:32], "big")
    assert il < N
    return (il + k) % N, I[32:]


def ckd_pub(K, c: bytes, i: int):
    if i >= HARD: raise ValueError("공개키로는 강화 파생 불가")
    I = hmac512(c, ser_compressed(K) + i.to_bytes(4, "big"))
    return point_add(point_mul(G, int.from_bytes(I[:32], "big")), K), I[32:]


# ── 경로 ────────────────────────────────────────────────────
def parse_path(path: str) -> list:
    """"m/84h/1h/0h/0/5" → [0x80000054, 0x80000001, 0x80000000, 0, 5].
    "m"으로 시작하지 않는 상대 경로("0/5")도 받는다."""
    parts = [p for p in path.strip().split("/") if p != ""]
    if parts and parts[0] == "m":
        parts = parts[1:]
    out = []
    for p in parts:
        hard = p[-1] in "hH'"
        n = int(p[:-1] if hard else p)
        if not 0 <= n < HARD: raise ValueError(f"자식 번호 범위 오류: {p}")
        out.append(n + HARD if hard else n)
    return out


def derive_priv(seed: bytes, path: str):
    """시드에서 경로를 따라 ckd_priv를 차례로 적용 → (개인키, 체인코드)."""
    k, c = master(seed)
    for i in parse_path(path):
        k, c = ckd_priv(k, c, i)
    return k, c


def derive_pub(K, c: bytes, path: str):
    """확장 공개키(K, c)에서 일반 파생 상대 경로("0/5")를 따라 → (공개키, 체인코드)."""
    for i in parse_path(path):
        K, c = ckd_pub(K, c, i)
    return K, c


def fingerprint(K) -> bytes:
    """HASH160(압축 공개키)의 앞 4바이트. 마스터 키면 '마스터 지문'."""
    return hash160(ser_compressed(K))[:4]


def derive_ext(seed: bytes, path: str):
    """직렬화에 필요한 정보까지 함께 파생 → (k, c, depth, parent_fp, child)."""
    k, c = master(seed)
    depth, parent_fp, child = 0, b"\x00" * 4, 0
    for i in parse_path(path):
        parent_fp = fingerprint(point_mul(G, k))
        k, c = ckd_priv(k, c, i)
        depth, child = depth + 1, i
    return k, c, depth, parent_fp, child


# ── 78바이트 직렬화 ─────────────────────────────────────────
def serialize(key, c: bytes, depth: int = 0, parent_fp: bytes = b"\x00" * 4,
              child: int = 0, testnet: bool = False) -> str:
    """key가 정수면 xprv/tprv, 점(튜플)이면 xpub/tpub.
    버전 4 ‖ 깊이 1 ‖ 부모 지문 4 ‖ 자식 번호 4 ‖ 체인코드 32 ‖ 키 33 → Base58Check."""
    if isinstance(key, int):
        ver = VERSIONS["tprv" if testnet else "xprv"]
        key_data = b"\x00" + key.to_bytes(32, "big")
    else:
        ver = VERSIONS["tpub" if testnet else "xpub"]
        key_data = ser_compressed(key)
    raw = ver + bytes([depth]) + parent_fp + child.to_bytes(4, "big") + c + key_data
    return b58check_encode(raw)


def derive_xprv(seed: bytes, path: str, testnet: bool = False) -> str:
    k, c, depth, parent_fp, child = derive_ext(seed, path)
    return serialize(k, c, depth, parent_fp, child, testnet)


def derive_xpub(seed: bytes, path: str, testnet: bool = False) -> str:
    k, c, depth, parent_fp, child = derive_ext(seed, path)
    return serialize(point_mul(G, k), c, depth, parent_fp, child, testnet)


def parse_extended(s: str) -> dict:
    """xprv/xpub/tprv/tpub 문자열 → dict. 형식이 틀리면 ValueError (BIP32 벡터 5의 검사)."""
    raw = b58check_decode(s)
    if len(raw) != 78: raise ValueError("길이가 78바이트가 아님")
    ver, depth, parent_fp = raw[:4], raw[4], raw[5:9]
    child, c, key_data = int.from_bytes(raw[9:13], "big"), raw[13:45], raw[45:]
    names = {v: k for k, v in VERSIONS.items()}
    if ver not in names: raise ValueError("알 수 없는 버전")
    name = names[ver]
    if depth == 0 and (parent_fp != b"\x00" * 4 or child != 0):
        raise ValueError("깊이 0인데 부모 지문이나 자식 번호가 0이 아님")
    private = name.endswith("prv")
    if private:
        if key_data[0] != 0x00: raise ValueError("개인키 접두 바이트가 0x00이 아님")
        key = int.from_bytes(key_data[1:], "big")
        if not 1 <= key < N: raise ValueError("개인키가 1..n-1 범위 밖")
    else:
        if key_data[0] not in (0x02, 0x03): raise ValueError("공개키 접두 바이트가 02/03이 아님")
        key = parse_pubkey(key_data)          # 곡선 위의 점인지 확인
    return {"version": name, "depth": depth, "parent_fp": parent_fp, "child": child,
            "chain_code": c, "key": key, "private": private, "testnet": name[0] == "t"}


def neuter(s: str) -> str:
    """xprv/tprv → 같은 위치의 xpub/tpub."""
    e = parse_extended(s)
    if not e["private"]: return s
    return serialize(point_mul(G, e["key"]), e["chain_code"], e["depth"], e["parent_fp"],
                     e["child"], e["testnet"])
