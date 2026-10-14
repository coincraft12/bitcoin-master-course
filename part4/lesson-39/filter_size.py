"""9-3 블록 필터 크기와 필터 헤더 사슬 (노드 없이 실행).

data/blockfilters.json은 Bitcoin Core 테스트 데이터(BIP158 basic 필터, testnet3 실제 블록 10개)다.
- 블록 크기 vs 필터 크기 비교 (getblockfilter의 filter)
- 필터 헤더 = dsha256(dsha256(필터) ‖ 이전 필터 헤더)  (BIP157, getblockfilter의 header)
  표시 순서 16진수는 블록 해시처럼 바이트를 뒤집은 것이다.

    python part4/lesson-39/filter_size.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.hashes import dsha256
from lib.block import parse_header

ROOT = pathlib.Path(__file__).resolve().parents[2]
rows = json.load(open(ROOT / "data" / "blockfilters.json"))[1:]


def filter_header(filter_hex: str, prev_header_hex: str) -> str:
    return dsha256(dsha256(bytes.fromhex(filter_hex)) + bytes.fromhex(prev_header_hex)[::-1])[::-1].hex()


print(f"{'높이':>8} {'블록(B)':>8} {'필터(B)':>8} {'비율':>6}  헤더 검증  비고")
for height, block_hash, block_hex, _prev_scripts, prev_hdr, filt, hdr, note in rows:
    assert parse_header(bytes.fromhex(block_hex)[:80])["hash"] == block_hash
    ok = filter_header(filt, prev_hdr) == hdr
    b, f = len(block_hex) // 2, len(filt) // 2
    print(f"{height:>8} {b:>8} {f:>8} {b / f:>6.1f}  {'OK' if ok else 'FAIL':>8}  {note[:40]}")
tot_b = sum(len(r[2]) // 2 for r in rows)
tot_f = sum(len(r[5]) // 2 for r in rows)
print(f"합계: 블록 {tot_b} B, 필터 {tot_f} B ({tot_b / tot_f:.0f}배 작다)")
