"""6강 미니 과제 정답: 상속형 Taproot 지갑 (s6-assign).

평소: 2-of-2 MuSig2 키 경로 (이번엔 자리표시 키 · 7-4에서 MuSig2 집계키로 바꿔 끼운다)
비상: "1년(52,560블록) 뒤 복구 키 단독" 리프 = and_v(v:pk(복구키),older(52560))

    python part3/lesson-27/assignment/solution/solution_inheritance.py          # 설계·디스크립터·주소 (노드 없이)
    python part3/lesson-27/assignment/solution/solution_inheritance.py --desc   # 디스크립터 한 줄만 (check_with_core.sh가 씀)
공개 테스트 니모닉(abandon ×11 + about) 키 · 실제 자금에 쓰지 말 것.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.ec import G, point_mul
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.taproot import tapleaf_hash, tweak_pubkey, control_block, taproot_tree
from lib.keys import p2tr_address
from descriptors import descsum_create, descsum_check      # Bitcoin Core test_framework (BIP380 체크섬)

BLOCKS = 52_560                    # 1년 ≈ 365일 × 144블록
SEQ_MAX = 65_535                   # nSequence 하위 16비트 상한 (BIP68)


def xonly(path):
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    return point_mul(G, derive_priv(seed, path)[0])[0].to_bytes(32, "big")


def script_num(n: int) -> bytes:
    if 1 <= n <= 16: return bytes([0x50 + n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "little")
    if b[-1] & 0x80: b += b"\x00"
    return bytes([len(b)]) + b


def leaf_script(recovery: bytes, blocks: int) -> bytes:
    """and_v(v:pk(R),older(n)) → <R> OP_CHECKSIGVERIFY <n> OP_CHECKSEQUENCEVERIFY (tapscript)"""
    return b"\x20" + recovery + b"\xad" + script_num(blocks) + b"\xb2"


def descriptor(internal: bytes, recovery: bytes, blocks: int) -> str:
    return descsum_create(f"tr({internal.hex()},and_v(v:pk({recovery.hex()}),older({blocks})))")


def address(internal: bytes, recovery: bytes, blocks: int, hrp="bcrt") -> str:
    leaves, root = taproot_tree((leaf_script(recovery, blocks), 0xc0))
    return p2tr_address(tweak_pubkey(internal, root)[1], hrp=hrp)


AGG = xonly("m/86h/1h/0h/0/0")      # 자리표시: 2-of-2 MuSig2 집계키 자리 (7-4)
REC = xonly("m/86h/1h/1h/0/0")      # 복구 키 (가족·상속인)

if __name__ == "__main__":
    if "--desc" in sys.argv:
        print(descriptor(AGG, REC, BLOCKS)); sys.exit()
    assert BLOCKS <= SEQ_MAX
    s = leaf_script(REC, BLOCKS)
    leaves, root = taproot_tree((s, 0xc0))
    parity, Q = tweak_pubkey(AGG, root)
    d = descriptor(AGG, REC, BLOCKS)
    print(f"타임락 {BLOCKS}블록 ≤ 상한 {SEQ_MAX}: {BLOCKS <= SEQ_MAX} (약 {BLOCKS * 10 // 60 // 24}일)")
    print("리프 스크립트", len(s), "B:", s.hex())
    print("리프 해시 = 머클 루트 (잎 하나):", tapleaf_hash(s).hex() == root.hex(), root.hex())
    print("디스크립터:", d)
    print("체크섬 검사:", descsum_check(d))
    print("주소 (regtest):", address(AGG, REC, BLOCKS))
    cb = control_block(AGG, 0xc0, leaves[0][2], root)
    print(f"복구 지출 witness: [복구키 서명 64B, 리프 스크립트 {len(s)}B, 컨트롤 블록 {len(cb)}B] · 입력 nSequence {BLOCKS} · 트랜잭션 version 2")
    print("평소 지출 witness: [집계키 서명 64B] — 단일 서명 지갑과 구분할 수 없다")
