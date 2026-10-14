"""교육용 구현. 실제 자금에 쓰지 말 것.

트랜잭션 파서와 직렬화 (5-2 · 3부 미니 과제).

    from lib.tx import dsha256, read_varint, parse_tx, write_varint, serialize_tx

- dsha256, read_varint, parse_tx      5-2 s52-code1~3 슬라이드 그대로
- write_varint, serialize_tx          3부 미니 과제(s7-assign 03)에서 추가하는 직렬화 함수

parse_tx가 돌려주는 dict (7-4 sighash.py도 이 형태를 그대로 받는다)
    version, segwit, vin, vout, locktime, txid, wtxid, size, weight, vsize
    vin[i]  = {"txid", "vout", "scriptSig"(hex), "sequence"} (+ SegWit이면 "witness": [hex, …])
    vout[i] = {"value_sat", "scriptPubKey"(hex)}
금액은 언제나 sat 정수다.
"""
import hashlib


def dsha256(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def read_varint(b: bytes, i: int):
    n = b[i]
    if n < 0xfd: return n, i + 1
    size = {0xfd: 2, 0xfe: 4, 0xff: 8}[n]
    return int.from_bytes(b[i+1:i+1+size], "little"), i + 1 + size


def parse_tx(hexstr: str) -> dict:
    b = bytes.fromhex(hexstr)
    version = int.from_bytes(b[0:4], "little")
    i = 4
    segwit = b[i] == 0x00 and b[i+1] == 0x01
    if segwit: i += 2
    io_start = i
    n_in, i = read_varint(b, i)
    vin = []
    for _ in range(n_in):
        prev_txid = b[i:i+32][::-1].hex(); i += 32   # 뒤집기
        vout = int.from_bytes(b[i:i+4], "little"); i += 4
        slen, i = read_varint(b, i)
        script_sig = b[i:i+slen].hex(); i += slen
        sequence = int.from_bytes(b[i:i+4], "little"); i += 4
        vin.append({"txid": prev_txid, "vout": vout, "scriptSig": script_sig, "sequence": sequence})
    n_out, i = read_varint(b, i); vout_list = []
    for _ in range(n_out):
        value = int.from_bytes(b[i:i+8], "little"); i += 8
        slen, i = read_varint(b, i)
        vout_list.append({"value_sat": value, "scriptPubKey": b[i:i+slen].hex()}); i += slen
    io_end = i
    if segwit:
        for txin in vin:
            n_items, i = read_varint(b, i); txin["witness"] = []
            for _ in range(n_items):
                ilen, i = read_varint(b, i)
                txin["witness"].append(b[i:i+ilen].hex()); i += ilen
    locktime = int.from_bytes(b[i:i+4], "little"); i += 4
    assert i == len(b), "남는 바이트가 있습니다"
    stripped = b[0:4] + b[io_start:io_end] + b[-4:]   # witness 제외
    weight = len(stripped) * 3 + len(b)
    return {
        "version": version, "segwit": segwit, "vin": vin, "vout": vout_list, "locktime": locktime,
        "txid": dsha256(stripped)[::-1].hex(),
        "wtxid": dsha256(b)[::-1].hex(),
        "size": len(b),                    # Core decoderawtransaction의 size (witness 포함 전체)
        "weight": weight,
        "vsize": (weight + 3) // 4,        # 올림
    }


# ---- 3부 미니 과제 (s7-assign 03): 직렬화 ----

def write_varint(n: int) -> bytes:
    """CompactSize 쓰기 (read_varint의 반대). 5-2 s52-varint 표 그대로."""
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff: return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")


def serialize_tx(tx: dict, include_witness: bool = True) -> bytes:
    """parse_tx 형태의 dict → 바이트. parse_tx(serialize_tx(t).hex())로 txid·wtxid·vsize를 다시 얻는다.

    witness 항목이 하나라도 있으면 SegWit 형식(marker 0x00, flag 0x01)으로 쓰고,
    include_witness=False면 txid 계산에 쓰는 레거시 형식(witness 제외)으로 쓴다.
    """
    has_witness = include_witness and any(txin.get("witness") for txin in tx["vin"])
    out = tx["version"].to_bytes(4, "little")
    if has_witness:
        out += b"\x00\x01"
    out += write_varint(len(tx["vin"]))
    for txin in tx["vin"]:
        script_sig = bytes.fromhex(txin["scriptSig"])
        out += bytes.fromhex(txin["txid"])[::-1] + txin["vout"].to_bytes(4, "little")
        out += write_varint(len(script_sig)) + script_sig + txin["sequence"].to_bytes(4, "little")
    out += write_varint(len(tx["vout"]))
    for o in tx["vout"]:
        spk = bytes.fromhex(o["scriptPubKey"])
        out += o["value_sat"].to_bytes(8, "little") + write_varint(len(spk)) + spk
    if has_witness:
        for txin in tx["vin"]:
            items = txin.get("witness", [])
            out += write_varint(len(items))
            for item in items:
                ib = bytes.fromhex(item)
                out += write_varint(len(ib)) + ib
    out += tx["locktime"].to_bytes(4, "little")
    return out
