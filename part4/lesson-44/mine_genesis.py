"""11-1 간이 채굴기와 난이도 조정 (노드 없이 실행).

1. 제네시스 헤더 앞 76바이트로 8·12·16·20비트 채굴 → 슬라이드 표의 nonce (236, 4200, 8603, 1085914)
2. 메인넷 가늠: 기대 시도 = 난이도 × 2^32, 파이썬 속도로 걸리는 시간
3. retarget 세 경우 (1주·4주·10주) + Bitcoin Core pow_tests.cpp의 조정 벡터 4건

    python part4/lesson-44/mine_genesis.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json, time
from fractions import Fraction
from lib.hashes import dsha256
from lib.block import mine, retarget, bits_to_target, next_bits, TWO_WEEKS

ROOT = pathlib.Path(__file__).resolve().parents[2]
prefix = bytes.fromhex(json.load(open(ROOT / "data" / "genesis_blocks.json", encoding="utf-8"))["main"]["header"])[:76]

print("== 1. 제네시스 헤더로 채굴 (시간은 컴퓨터마다 다름) ==")
for k in (8, 12, 16, 20):
    nonce, h, sec = mine(prefix, k)
    print(f"{k:>2}비트 nonce={nonce:>9,} hash={h[:12]}…  {sec:6.2f}s")

print("== 2. 메인넷이라면 ==")
n = 200_000
t0 = time.time()
for i in range(n):
    dsha256(prefix + i.to_bytes(4, "little"))
rate = n / (time.time() - t0)
expected = int(132.7e12) * 2**32
print(f"기대 시도 = 132.7T × 2^32 ≈ {expected:.2e}")
print(f"이 컴퓨터의 파이썬 속도 ≈ {rate:,.0f} 해시/초 → 약 {expected / rate / 3.15576e7:.1e} 년 (실행마다 다름)")
print(f"슬라이드 가정 57만 해시/초 → 약 {expected / 570_000 / 3.15576e7:.1e} 년")

print("== 3. retarget ==")
old = bits_to_target(0x1c05a3f4)
week = 7 * 24 * 3600
for label, span in (("1주", week), ("4주", 4 * week), ("10주", 10 * week)):
    print(f"2016블록이 {label:>3} → 타깃 ×{Fraction(retarget(old, span), old)}")
print("Bitcoin Core pow_tests.cpp 벡터 (메인넷 파라미터, 마지막 건은 4배 상한 시험용 시각):")
for v in json.load(open(ROOT / "data" / "pow_retarget_vectors.json", encoding="utf-8"))["vectors"]:
    span = v["last_block_time"] - v["first_block_time"]
    got = next_bits(v["old_bits"], v["first_block_time"], v["last_block_time"])
    print(f"  높이 {v['last_height'] + 1:>6}: 실제 {span / TWO_WEEKS:5.2f} × 2주, bits {v['old_bits']:#010x} → {got:#010x}"
          f" ({'일치' if got == v['expected_bits'] else '불일치'})")
