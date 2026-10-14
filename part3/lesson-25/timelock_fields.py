"""6-3 노드 없이: nLockTime·nSequence 해석과 CLTV·CSV 잠금 스크립트 바이트 (s63-locktime, s63-seq, s63-cltv).

실행: python part3/lesson-25/timelock_fields.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, point_mul
from lib.keys import ser_compressed

LOCKTIME_THRESHOLD = 500_000_000


def locktime(v: int) -> str:
    if v == 0: return "0 → 즉시 유효"
    if v < LOCKTIME_THRESHOLD: return f"{v} → 블록 높이 {v} 이후 블록부터 포함 가능"
    return f"{v} → 유닉스 시간 {v} 이후 (직전 11블록 중앙값 시간 MTP 기준, BIP113)"


def sequence(v: int) -> str:
    if v == 0xffffffff: return f"0x{v:08x} → 최종: nLockTime 무시, RBF 신호 없음, 상대 타임락 없음"
    notes = []
    if v < 0xfffffffe: notes.append("RBF 신호(8-3)")
    if v & (1 << 31):
        notes.append("31번 비트 1 → 상대 타임락 비활성")
    else:
        unit = "512초 단위 시간" if v & (1 << 22) else "블록 수"
        n = v & 0xffff
        extra = f" = {n * 512:,}초 ≈ {n * 512 // 3600}시간" if v & (1 << 22) else (" = 확정 후 약 하루" if n == 144 else "")
        notes.append(f"상대 타임락 {n} ({unit}){extra}")
    return f"0x{v:08x} → " + ", ".join(notes)


def script_num(n: int) -> bytes:
    """스크립트 숫자: 리틀 엔디안 최소 바이트, 최상위 비트가 1이면 0x00을 덧붙인다(부호 비트). 1~16은 OP_1~OP_16."""
    if 1 <= n <= 16: return bytes([0x50 + n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "little")
    if b[-1] & 0x80: b += b"\x00"
    return bytes([len(b)]) + b


pub = ser_compressed(point_mul(G, 1))     # 예시 공개키 (개인키 1 · 실제 자금 금지)
print("nLockTime")
for v in (0, 800_000, 1_700_000_000):
    print("  ", locktime(v))
print("nSequence (BIP68)")
for v in (0xffffffff, 0xfffffffd, 144, (1 << 22) | 169, 1 << 31):
    print("  ", sequence(v))
H, N = 820_000, 144
cltv = script_num(H) + b"\xb1\x75" + bytes([33]) + pub + b"\xac"
csv = script_num(N) + b"\xb2\x75" + bytes([33]) + pub + b"\xac"
print(f"\n<{H}> OP_CHECKLOCKTIMEVERIFY OP_DROP <공개키> OP_CHECKSIG")
print("  ", cltv.hex())
print(f"<{N}> OP_CHECKSEQUENCEVERIFY OP_DROP <공개키> OP_CHECKSIG")
print("  ", csv.hex())
print("상대 타임락 상한 65,535 블록(약 455일) · 1년 ≈ 52,560블록은 older(52560)으로 표현 가능:", script_num(52_560).hex())
