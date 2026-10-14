"""교육용 구현. 실제 자금에 쓰지 말 것.

서명 해시(서명할 메시지) 계산 (7-4).

    from lib.sighash import taproot_sighash, bip143_sighash, legacy_sighash, p2wpkh_script_code

- taproot_sighash(tx, prevouts, idx, hash_type=0x00)   BIP341 키 경로·annex 없음 (s74-code1·2 슬라이드 그대로)
                                                     prevouts = [(금액 sat, scriptPubKey bytes)] 모든 입력
- bip143_sighash(tx, idx, script_code, amount, hash_type=0x01)   SegWit v0 (s74-amount "BIP143")
- legacy_sighash(tx, idx, script_code, hash_type=0x01)            레거시 (s74-amount "LEGACY", 6-1 checksig)

tx는 lib/tx.py parse_tx의 결과 dict다. 세 함수 모두 32바이트를 돌려준다.
- Taproot: 그대로 BIP340 서명의 msg로 쓴다.
- BIP143·레거시: ECDSA의 z = int.from_bytes(결과, "big"). Core가 화면에 찍는 값은 결과를 뒤집은 hex다.
script_code는 길이 접두어 없는 스크립트 본문이다. P2WPKH는 p2wpkh_script_code(공개키해시 20B).
"""
import hashlib
from lib.hashes import dsha256
from lib.taproot import tagged_hash, ser_compact


# ---- BIP341 (s74-code1·2) ----

def sha(b): return hashlib.sha256(b).digest()


def outpoint(i):
    return bytes.fromhex(i["txid"])[::-1] + i["vout"].to_bytes(4, "little")


def ser_out(o):
    spk = bytes.fromhex(o["scriptPubKey"])
    return o["value_sat"].to_bytes(8, "little") + ser_compact(len(spk)) + spk


def taproot_sighash(tx, prevouts, idx, hash_type=0x00):   # prevouts: [(sat, spk)]
    out_type, anyone = hash_type & 0x03, hash_type & 0x80
    m = bytes([0x00, hash_type])
    m += tx["version"].to_bytes(4, "little") + tx["locktime"].to_bytes(4, "little")
    if not anyone:
        m += sha(b"".join(outpoint(i) for i in tx["vin"]))
        m += sha(b"".join(a.to_bytes(8, "little") for a, _ in prevouts))
        m += sha(b"".join(ser_compact(len(s)) + s for _, s in prevouts))
        m += sha(b"".join(i["sequence"].to_bytes(4, "little") for i in tx["vin"]))
    if out_type not in (0x02, 0x03):
        m += sha(b"".join(ser_out(o) for o in tx["vout"]))
    m += bytes([0x00])                                   # spend_type
    if anyone:
        i = tx["vin"][idx]; a, s = prevouts[idx]
        m += outpoint(i) + a.to_bytes(8, "little") + ser_compact(len(s)) + s
        m += i["sequence"].to_bytes(4, "little")
    else:
        m += idx.to_bytes(4, "little")
    if out_type == 0x03:
        m += sha(ser_out(tx["vout"][idx]))
    return tagged_hash("TapSighash", m)


# ---- 공통 보조 ----

SIGHASH_ALL, SIGHASH_NONE, SIGHASH_SINGLE, SIGHASH_ANYONECANPAY = 0x01, 0x02, 0x03, 0x80


def _varint(n: int) -> bytes:
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff: return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")


def p2wpkh_script_code(pubkey_hash: bytes) -> bytes:
    """P2WPKH의 scriptCode = P2PKH 잠금 스크립트 모양 OP_DUP OP_HASH160 <20B> OP_EQUALVERIFY OP_CHECKSIG (BIP143)."""
    return b"\x76\xa9\x14" + pubkey_hash + b"\x88\xac"


# ---- BIP143 (SegWit v0) ----

def bip143_sighash(tx, idx, script_code: bytes, amount: int, hash_type=0x01) -> bytes:
    base, anyone = hash_type & 0x1f, hash_type & SIGHASH_ANYONECANPAY
    zero = b"\x00" * 32
    hash_prevouts = dsha256(b"".join(outpoint(i) for i in tx["vin"])) if not anyone else zero
    hash_sequence = (dsha256(b"".join(i["sequence"].to_bytes(4, "little") for i in tx["vin"]))
                     if not anyone and base not in (SIGHASH_NONE, SIGHASH_SINGLE) else zero)
    if base not in (SIGHASH_NONE, SIGHASH_SINGLE):
        hash_outputs = dsha256(b"".join(ser_out(o) for o in tx["vout"]))
    elif base == SIGHASH_SINGLE and idx < len(tx["vout"]):
        hash_outputs = dsha256(ser_out(tx["vout"][idx]))
    else:
        hash_outputs = zero
    i = tx["vin"][idx]
    m = tx["version"].to_bytes(4, "little") + hash_prevouts + hash_sequence
    m += outpoint(i) + _varint(len(script_code)) + script_code
    m += amount.to_bytes(8, "little") + i["sequence"].to_bytes(4, "little")
    m += hash_outputs + tx["locktime"].to_bytes(4, "little")
    m += (hash_type & 0xffffffff).to_bytes(4, "little")
    return dsha256(m)


# ---- 레거시 ----

def _remove_codeseparators(script: bytes) -> bytes:
    """scriptCode에서 OP_CODESEPARATOR(0xab)를 뺀다. push 데이터 안의 0xab는 건드리지 않는다."""
    out, i = b"", 0
    while i < len(script):
        op = script[i]; start = i; i += 1
        if 0x01 <= op <= 0x4b: i += op
        elif op == 0x4c: i += 1 + (script[i] if i < len(script) else 0)
        elif op == 0x4d: i += 2 + int.from_bytes(script[i:i+2], "little")
        elif op == 0x4e: i += 4 + int.from_bytes(script[i:i+4], "little")
        if op != 0xab:
            out += script[start:i]
    return out


def legacy_sighash(tx, idx, script_code: bytes, hash_type=0x01) -> bytes:
    """Bitcoin Core SignatureHash(SigVersion::BASE)와 같은 계산.

    서명하는 입력의 scriptSig 자리에 script_code(보통 이전 출력의 scriptPubKey)를 넣고 나머지는 비운 사본을
    hash_type 4바이트와 함께 SHA256 두 번. 옛 구현의 특이점(입력 번호 범위 밖, SINGLE인데 같은 번호 출력 없음
    → 1)도 Core와 같게 둔다. 서명 자체를 scriptCode에서 지우는 FindAndDelete는 스크립트 실행 쪽 일이라 여기서 하지 않는다.
    """
    one = (1).to_bytes(32, "little")
    base, anyone = hash_type & 0x1f, hash_type & SIGHASH_ANYONECANPAY
    if idx >= len(tx["vin"]):
        return one
    if base == SIGHASH_SINGLE and idx >= len(tx["vout"]):
        return one
    code = _remove_codeseparators(script_code)
    inputs = [idx] if anyone else range(len(tx["vin"]))
    m = tx["version"].to_bytes(4, "little") + _varint(len(inputs))
    for n in inputs:
        i = tx["vin"][n]
        sc = code if n == idx else b""
        seq = i["sequence"] if (n == idx or base not in (SIGHASH_NONE, SIGHASH_SINGLE)) else 0
        m += outpoint(i) + _varint(len(sc)) + sc + seq.to_bytes(4, "little")
    if base == SIGHASH_NONE:
        m += _varint(0)
    elif base == SIGHASH_SINGLE:
        m += _varint(idx + 1)
        m += (b"\xff" * 8 + b"\x00") * idx              # 앞 출력은 금액 -1, 빈 스크립트
        m += ser_out(tx["vout"][idx])
    else:
        m += _varint(len(tx["vout"])) + b"".join(ser_out(o) for o in tx["vout"])
    m += tx["locktime"].to_bytes(4, "little") + (hash_type & 0xffffffff).to_bytes(4, "little")
    return dsha256(m)
