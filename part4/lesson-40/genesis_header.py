"""10-1 제네시스 헤더 해석과 변경 저항 (노드 없이 실행).

data/genesis_blocks.json의 헤더 80바이트(Bitcoin Core chainparams.cpp 값으로 조립)를
parse_header로 해석하고, 메인넷과 regtest의 타깃 자릿수를 비교하고,
머클 루트 1바이트를 바꾸면 해시와 작업증명이 어떻게 되는지 본다(s101-chain).

    python part4/lesson-40/genesis_header.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.block import parse_header, bits_to_target, check_pow, difficulty

ROOT = pathlib.Path(__file__).resolve().parents[2]
G = json.load(open(ROOT / "data" / "genesis_blocks.json", encoding="utf-8"))

for net in ("main", "regtest"):
    raw = bytes.fromhex(G[net]["header"])
    hdr = parse_header(raw)
    print(f"== {net} 제네시스 ({len(raw)}바이트) ==")
    print(f"version {hdr['version']} · time {hdr['time']} · bits {hdr['bits']:#010x} · nonce {hdr['nonce']}")
    print(f"prev        {hdr['prev']}")
    print(f"merkle_root {hdr['merkle_root']}")
    print(f"hash        {hdr['hash']}")
    t = bits_to_target(hdr["bits"])
    print(f"target      {t:064x}")
    print(f"check_pow {check_pow(raw)} · 타깃 비트 길이 {t.bit_length()} · 난이도 {difficulty(hdr['bits']):.3g}")

print("== 변경 저항: 메인넷 제네시스의 머클 루트 1바이트를 바꾸면 ==")
raw = bytearray.fromhex(G["main"]["header"])
raw[36] ^= 0x01
bad = parse_header(bytes(raw))
print(f"hash        {bad['hash']}")
print(f"check_pow {check_pow(bytes(raw))} → 다시 채굴해야 하고, 다음 블록의 prev_block_hash와도 맞지 않는다")
