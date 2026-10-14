"""교육용 구현. 실제 자금에 쓰지 말 것.

Taproot 출력키·스크립트 트리 (6-4, 6-5 · 7-3에서 lift_x 보강).

    from lib.taproot import tagged_hash, lift_x, output_key          # 6-4 (s64-code)
    from lib.taproot import ser_compact, tapleaf_hash, tapbranch_hash, verify_script_path   # 6-5 (s65-code)
    from lib.taproot import NUMS_H, nums_h, taproot_tree, tweak_pubkey, control_block, p2tr_script_pubkey

- 6-4 s64-code: tagged_hash, lift_x, output_key 그대로. 2부(4-3 BIP86 주소)에서 먼저 쓴다.
- 7-3 s73-code1: lift_x에 "x ≥ FIELD_P면 실패" 한 줄 추가 (BIP340 테스트 벡터 하나가 이 경우를 거른다).
- 6-5 s65-code: ser_compact, tapleaf_hash, tapbranch_hash, verify_script_path 그대로.
- 6-5 s65-tree·s65-witness·s65-nums를 코드로 옮긴 보조 함수: taproot_tree(트리 → 잎·머클 경로·루트),
  tweak_pubkey(출력키와 y 패리티), control_block, NUMS_H/nums_h, p2tr_script_pubkey.

트리 표기 (BIP341 wallet-test-vectors의 scriptTree와 같은 모양)
    잎   = {"script": bytes 또는 hex, "leafVersion": 0xc0}   또는 (script_bytes, leaf_version)
    가지 = [왼쪽, 오른쪽]
    트리 없음 = None
"""
import hashlib
from lib.ec import G, N, FIELD_P, point_add, point_mul
from lib import segwit_addr          # BIP350 참조 구현


def tagged_hash(tag: str, msg: bytes) -> bytes:
    t = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(t + t + msg).digest()


def lift_x(x: int):
    if x >= FIELD_P: raise ValueError("x가 필드 크기 이상")        # 7-3에서 추가한 한 줄
    y_sq = (pow(x, 3, FIELD_P) + 7) % FIELD_P
    y = pow(y_sq, (FIELD_P + 1) // 4, FIELD_P)
    if pow(y, 2, FIELD_P) != y_sq: raise ValueError("곡선 위의 x가 아님")
    return (x, y if y % 2 == 0 else FIELD_P - y)   # 짝수 y 선택


def output_key(internal_xonly: bytes, merkle_root: bytes = b"") -> bytes:
    P = lift_x(int.from_bytes(internal_xonly, "big"))
    t = int.from_bytes(tagged_hash("TapTweak", internal_xonly + merkle_root), "big")
    assert t < N
    return point_add(P, point_mul(G, t))[0].to_bytes(32, "big")


# ---- 6-5 s65-code: 약속을 직접 검증 ----

def ser_compact(n): return bytes([n]) if n < 0xfd else b"\xfd" + n.to_bytes(2, "little")


def tapleaf_hash(script, leaf_version=0xc0):
    return tagged_hash("TapLeaf", bytes([leaf_version]) + ser_compact(len(script)) + script)


def tapbranch_hash(a, b): return tagged_hash("TapBranch", min(a, b) + max(a, b))


def verify_script_path(output_xonly: bytes, script: bytes, control: bytes) -> bool:
    leaf_version = control[0] & 0xfe
    internal = control[1:33]
    k = tapleaf_hash(script, leaf_version)
    for i in range(33, len(control), 32):
        k = tapbranch_hash(k, control[i:i+32])
    return output_key(internal, k) == output_xonly   # 패리티 검사는 단순화로 생략


# ---- 6-5 s65-tree · s65-witness · s65-nums를 코드로 ----

# BIP341이 예로 든 NUMS 점 H의 x좌표 = lift_x(SHA256(G의 비압축 직렬화)) (s65-nums)
NUMS_H = bytes.fromhex("50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0")


def nums_h() -> bytes:
    """NUMS_H를 직접 계산한다: SHA256(0x04‖G.x‖G.y)를 x로 보고 lift_x (곡선 위에 있음을 확인)."""
    h = hashlib.sha256(b"\x04" + G[0].to_bytes(32, "big") + G[1].to_bytes(32, "big")).digest()
    return lift_x(int.from_bytes(h, "big"))[0].to_bytes(32, "big")


def _leaf(node):
    if isinstance(node, dict):
        s = node["script"]
        return (bytes.fromhex(s) if isinstance(s, str) else s), node.get("leafVersion", 0xc0)
    script, leaf_version = node
    return script, leaf_version


def taproot_tree(tree):
    """트리 → ([(leaf_version, script, 머클 경로 bytes)], 루트 해시). 잎 순서는 왼쪽부터(BIP341 참조 구현과 같다).

    머클 경로 = 그 잎에서 루트까지 올라가며 만나는 형제 해시들(32B × 깊이). 컨트롤 블록 뒷부분이 된다.
    """
    if tree is None:
        return [], b""
    if isinstance(tree, list):
        if len(tree) != 2:
            raise ValueError("가지는 [왼쪽, 오른쪽] 두 개여야 한다")
        left, h_left = taproot_tree(tree[0])
        right, h_right = taproot_tree(tree[1])
        leaves = [(v, s, path + h_right) for v, s, path in left] + \
                 [(v, s, path + h_left) for v, s, path in right]
        return leaves, tapbranch_hash(h_left, h_right)
    script, leaf_version = _leaf(tree)
    return [(leaf_version, script, b"")], tapleaf_hash(script, leaf_version)


def tweak_pubkey(internal_xonly: bytes, merkle_root: bytes = b"") -> tuple:
    """(출력키 y 패리티 0/1, 출력키 x 32B). output_key와 같은 계산에 패리티를 함께 돌려준다."""
    P = lift_x(int.from_bytes(internal_xonly, "big"))
    t = int.from_bytes(tagged_hash("TapTweak", internal_xonly + merkle_root), "big")
    if t >= N: raise ValueError("조정값이 N 이상")
    Q = point_add(P, point_mul(G, t))
    return Q[1] % 2, Q[0].to_bytes(32, "big")


def control_block(internal_xonly: bytes, leaf_version: int, path: bytes, merkle_root: bytes) -> bytes:
    """컨트롤 블록 = (리프 버전 | 출력키 y 패리티) 1B ‖ 내부키 32B ‖ 머클 경로 (s65-witness 표)."""
    parity, _ = tweak_pubkey(internal_xonly, merkle_root)
    return bytes([leaf_version | parity]) + internal_xonly + path


def p2tr_script_pubkey(output_xonly: bytes) -> bytes:
    """P2TR 잠금 스크립트 0x51 0x20 ‖ 출력키 (OP_1 · 32바이트 push)."""
    return b"\x51\x20" + output_xonly
