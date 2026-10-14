"""교육용 구현. 실제 자금에 쓰지 말 것.

블록 헤더·머클 트리·작업증명·보조금 (10강·11강).

    from lib.block import parse_header, bits_to_target, check_pow, merkle_root
    from lib.block import mine, retarget, subsidy, total_supply

슬라이드 코드(10-1 s101-lab, 10-2 s102-lab, 11-1 s111-lab1, 11-2 s112-lab)는 그대로 두고,
그 아래에 저장소가 보탠 함수(직렬화, target→bits, 난이도, 머클 증명, gettxoutproof 해석,
버전 비트)를 붙였다.

바이트 순서 규칙
- 헤더 안의 해시(prev, merkle_root)와 블록 해시는 내부 순서로 저장되고, 표시할 때 뒤집는다(5-1 txid와 같음).
- 정수 필드(version, time, bits, nonce)는 리틀 엔디안.
"""
from lib.hashes import dsha256


# ── 10-1 블록 헤더 (s101-lab) ─────────────────────────────────────────────

def parse_header(h: bytes) -> dict:
    assert len(h) == 80
    le = lambda b: int.from_bytes(b, "little")
    return {"version": le(h[0:4]),
        "prev": h[4:36][::-1].hex(),
        "merkle_root": h[36:68][::-1].hex(),
        "time": le(h[68:72]), "bits": le(h[72:76]),
        "nonce": le(h[76:80]),
        "hash": dsha256(h)[::-1].hex()}


def bits_to_target(bits: int) -> int:
    exp, mant = bits >> 24, bits & 0xFFFFFF
    return mant * (1 << (8 * (exp - 3)))


def check_pow(h: bytes) -> bool:
    hdr = parse_header(h)
    target = bits_to_target(hdr["bits"])
    return int(hdr["hash"], 16) <= target


# ── 10-2 머클 루트 (s102-lab) ─────────────────────────────────────────────

def merkle_root(txids: list[str]) -> str:
    layer = [bytes.fromhex(t)[::-1] for t in txids]
    if not layer: raise ValueError("빈 목록")
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [dsha256(layer[i] + layer[i + 1])
                 for i in range(0, len(layer), 2)]
    return layer[0][::-1].hex()


# ── 11-1 간이 채굴기와 난이도 조정 (s111-lab1) ────────────────────────────
import time


def mine(prefix76: bytes, zero_bits: int, max_tries: int = 2**32):
    target = 1 << (256 - zero_bits)
    t0 = time.time()
    for nonce in range(max_tries):
        h = dsha256(prefix76 + nonce.to_bytes(4, "little"))[::-1]
        if int.from_bytes(h, "big") < target:
            return nonce, h.hex(), time.time() - t0
    return None


POW_LIMIT = 0x00000000FFFF << 208          # 메인넷 최대 타깃
TWO_WEEKS = 2016 * 600


def retarget(old_target: int, actual_timespan: int) -> int:
    actual = max(TWO_WEEKS // 4, min(actual_timespan, TWO_WEEKS * 4))
    return min(old_target * actual // TWO_WEEKS, POW_LIMIT)


# ── 11-2 보조금 (s112-lab) ────────────────────────────────────────────────
COIN = 100_000_000


def subsidy(height: int, interval: int = 210_000) -> int:
    halvings = height // interval
    return 0 if halvings >= 64 else (50 * COIN) >> halvings


def total_supply(interval: int = 210_000) -> int:
    total, h = 0, 0
    while (s := subsidy(h, interval)) > 0:
        total += s * interval
        h += interval
    return total


# ══ 여기부터 저장소가 보탠 함수 ════════════════════════════════════════════

HEADER_FIELDS = ("version", "prev", "merkle_root", "time", "bits", "nonce")


def serialize_header(fields: dict) -> bytes:
    """parse_header의 역. version·prev·merkle_root·time·bits·nonce로 80바이트를 만든다.
    prev와 merkle_root는 표시 순서 16진수 문자열(parse_header가 돌려주는 형태)."""
    h = (fields["version"].to_bytes(4, "little")
         + bytes.fromhex(fields["prev"])[::-1]
         + bytes.fromhex(fields["merkle_root"])[::-1]
         + fields["time"].to_bytes(4, "little")
         + fields["bits"].to_bytes(4, "little")
         + fields["nonce"].to_bytes(4, "little"))
    assert len(h) == 80
    return h


def header_hash(h: bytes) -> str:
    """블록 해시(표시 순서 16진수) = dsha256(헤더 80바이트)를 뒤집은 것."""
    assert len(h) == 80
    return dsha256(h)[::-1].hex()


def target_to_bits(target: int) -> int:
    """타깃 → bits(압축 표기). Bitcoin Core arith_uint256::GetCompact와 같은 규칙.
    가수는 3바이트이고 최상위 비트(0x800000)는 부호 비트라, 그 비트가 켜지면 지수를 하나 올린다.
    그래서 bits_to_target(target_to_bits(t))는 t의 상위 3바이트만 남긴 값이다(하위는 버려진다)."""
    if target < 0:
        raise ValueError("음수 타깃")
    size = (target.bit_length() + 7) // 8
    if size <= 3:
        compact = target << (8 * (3 - size))
    else:
        compact = target >> (8 * (size - 3))
    if compact & 0x00800000:
        compact >>= 8
        size += 1
    return (size << 24) | (compact & 0x007FFFFF)


DIFF1_TARGET = bits_to_target(0x1d00ffff)   # 난이도 1 타깃 = POW_LIMIT


def difficulty(bits: int) -> float:
    """"난이도" 숫자 = 최대 타깃(난이도 1) ÷ 현재 타깃 (11-1). 높을수록 어렵다. getdifficulty와 같은 정의."""
    return DIFF1_TARGET / bits_to_target(bits)


def block_work(bits: int) -> int:
    """블록 하나의 기대 작업량 = 2^256 ÷ (타깃 + 1). 10-3 "가장 무거운 체인"은 이 값을 합산한다
    (Bitcoin Core GetBlockProof, getblockheader의 chainwork)."""
    return (1 << 256) // (bits_to_target(bits) + 1)


def next_bits(old_bits: int, first_block_time: int, last_block_time: int) -> int:
    """2016블록 구간의 첫·마지막 블록 time으로 다음 bits를 계산한다(11-1 공식 + Core처럼 compact로 반올림).
    retarget()에 실제 시간 = 마지막 − 첫(2015개 간격, time warp 특성 그대로)을 넣는다."""
    return target_to_bits(retarget(bits_to_target(old_bits), last_block_time - first_block_time))


# ── 머클 증명 (10-2 s102-proof) ──────────────────────────────────────────

def merkle_proof(txids: list[str], index: int) -> list[str]:
    """txids[index]가 루트까지 올라가는 길의 형제 해시 목록(아래층부터, 내부 순서 16진수).
    홀수 층에서 마지막 원소의 형제는 자기 자신(복제)이다."""
    if not 0 <= index < len(txids):
        raise IndexError("index 범위 밖")
    layer = [bytes.fromhex(t)[::-1] for t in txids]
    proof = []
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        proof.append(layer[index ^ 1].hex())
        layer = [dsha256(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
        index //= 2
    return proof


def root_from_proof(txid: str, index: int, proof: list[str]) -> str:
    """내 txid와 형제 해시를 차례로 합쳐 루트(표시 순서)를 계산한다. index의 각 비트가 왼쪽/오른쪽을 정한다."""
    h = bytes.fromhex(txid)[::-1]
    for sib in proof:
        s = bytes.fromhex(sib)
        h = dsha256(s + h) if index & 1 else dsha256(h + s)
        index >>= 1
    return h[::-1].hex()


def verify_merkle_proof(txid: str, index: int, proof: list[str], root: str) -> bool:
    return root_from_proof(txid, index, proof) == root


# ── gettxoutproof 해석 (CMerkleBlock = 헤더 + 부분 머클 트리, BIP37 형식) ──

def _read_varint(b: bytes, i: int):
    n = b[i]
    if n < 0xfd:
        return n, i + 1
    k = {0xfd: 2, 0xfe: 4, 0xff: 8}[n]
    return int.from_bytes(b[i + 1:i + 1 + k], "little"), i + 1 + k


def _varint(n: int) -> bytes:
    if n < 0xfd:
        return bytes([n])
    if n <= 0xffff:
        return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff:
        return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")


def _tree_width(n_tx: int, height: int) -> int:
    return (n_tx + (1 << height) - 1) >> height


def _tree_height(n_tx: int) -> int:
    height = 0
    while _tree_width(n_tx, height) > 1:
        height += 1
    return height


def parse_merkleblock(proof_hex: str) -> dict:
    """gettxoutproof의 결과 hex → {"header": 80바이트, "n_tx", "hashes": [내부 순서 bytes], "bits": [bool]}.
    앞 80바이트가 블록 헤더다(10-1 parse_header로 해석)."""
    b = bytes.fromhex(proof_hex)
    header = b[:80]
    n_tx = int.from_bytes(b[80:84], "little")
    n_hash, i = _read_varint(b, 84)
    hashes = [b[i + 32 * k:i + 32 * (k + 1)] for k in range(n_hash)]
    i += 32 * n_hash
    n_bytes, i = _read_varint(b, i)
    flag = b[i:i + n_bytes]
    if i + n_bytes != len(b):
        raise ValueError("남는 바이트가 있다")
    bits = [bool(flag[k // 8] >> (k % 8) & 1) for k in range(8 * n_bytes)]
    return {"header": header, "n_tx": n_tx, "hashes": hashes, "bits": bits}


def extract_matches(pmt: dict) -> tuple:
    """부분 머클 트리에서 루트와 증명 대상 txid를 꺼낸다 (Core CPartialMerkleTree::ExtractMatches와 같은 순회).
    반환: (merkle_root 표시 순서, [(위치, txid 표시 순서), ...]). 형식이 틀리면 ValueError."""
    n_tx, hashes, bits = pmt["n_tx"], pmt["hashes"], pmt["bits"]
    if n_tx == 0 or len(hashes) > n_tx:
        raise ValueError("트랜잭션 수가 이상하다")
    used = {"bits": 0, "hash": 0}
    matches = []

    def walk(height: int, pos: int) -> bytes:
        if used["bits"] >= len(bits):
            raise ValueError("플래그 비트 부족")
        parent_of_match = bits[used["bits"]]
        used["bits"] += 1
        if height == 0 or not parent_of_match:
            if used["hash"] >= len(hashes):
                raise ValueError("해시 부족")
            h = hashes[used["hash"]]
            used["hash"] += 1
            if height == 0 and parent_of_match:
                matches.append((pos, h[::-1].hex()))
            return h
        left = walk(height - 1, pos * 2)
        if pos * 2 + 1 < _tree_width(n_tx, height - 1):
            right = walk(height - 1, pos * 2 + 1)
            if right == left:                       # CVE-2012-2459 대응: 왼쪽과 같은 오른쪽은 거부
                raise ValueError("왼쪽과 오른쪽 해시가 같다")
        else:
            right = left
        return dsha256(left + right)

    root = walk(_tree_height(n_tx), 0)
    if (used["bits"] + 7) // 8 != (len(bits) + 7) // 8 or used["hash"] != len(hashes):
        raise ValueError("쓰지 않은 비트·해시가 남았다")
    return root[::-1].hex(), matches


def build_merkleblock(header: bytes, txids: list[str], match: set) -> str:
    """txids(블록 순서) 중 match(txid 집합)를 증명하는 merkleblock hex를 만든다 (gettxoutproof와 같은 형식).
    Core CPartialMerkleTree::TraverseAndBuild와 같은 순회."""
    leaves = [bytes.fromhex(t)[::-1] for t in txids]
    flags = [t in match for t in txids]
    n_tx = len(leaves)
    hashes, bits = [], []

    def calc(height: int, pos: int) -> bytes:
        if height == 0:
            return leaves[pos]
        left = calc(height - 1, pos * 2)
        right = calc(height - 1, pos * 2 + 1) if pos * 2 + 1 < _tree_width(n_tx, height - 1) else left
        return dsha256(left + right)

    def build(height: int, pos: int):
        parent = any(flags[pos << height:min((pos + 1) << height, n_tx)])
        bits.append(parent)
        if height == 0 or not parent:
            hashes.append(calc(height, pos))
        else:
            build(height - 1, pos * 2)
            if pos * 2 + 1 < _tree_width(n_tx, height - 1):
                build(height - 1, pos * 2 + 1)

    build(_tree_height(n_tx), 0)
    flag = bytearray((len(bits) + 7) // 8)
    for k, v in enumerate(bits):
        flag[k // 8] |= int(v) << (k % 8)
    out = (header + n_tx.to_bytes(4, "little") + _varint(len(hashes)) + b"".join(hashes)
           + _varint(len(flag)) + bytes(flag))
    return out.hex()


# ── 버전 비트 (11-5 BIP9) ────────────────────────────────────────────────
VERSIONBITS_TOP_BITS = 0x20000000
VERSIONBITS_TOP_MASK = 0xE0000000


def signals_bit(version: int, bit: int) -> bool:
    """헤더 version이 BIP9 형식(상위 3비트 001)이고 bit번 비트가 켜져 있으면 True."""
    return (version & VERSIONBITS_TOP_MASK) == VERSIONBITS_TOP_BITS and bool(version >> bit & 1)
