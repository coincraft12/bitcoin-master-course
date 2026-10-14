"""10-2 머클 트리 (노드 없이 실행).

1. 메인넷 블록 100,000의 txid 4개 → 공개된 머클 루트 f3e94742…와 일치 (data/block100000.json)
2. 포함 증명: 형제 해시만으로 루트 재계산, 트랜잭션 수별 증명 해시 수(log₂n)
3. 홀수 복제의 함정: [A, B, C]와 [A, B, C, C]의 루트가 같다 (CVE-2012-2459)

    python part4/lesson-41/merkle_offline.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.block import merkle_root, merkle_proof, verify_merkle_proof, parse_header

ROOT = pathlib.Path(__file__).resolve().parents[2]
B = json.load(open(ROOT / "data" / "block100000.json"))
txids = B["txids"]

print("== 1. 블록 100,000 ==")
for t in txids:
    print(" ", t)
root = merkle_root(txids)
print("계산한 루트  ", root)
print("헤더의 루트  ", parse_header(bytes.fromhex(B["header"]))["merkle_root"], root == B["merkle_root"])

print("== 2. 포함 증명: 세 번째 트랜잭션(index 2) ==")
proof = merkle_proof(txids, 2)
for i, h in enumerate(proof):
    print(f"  형제 {i} (내부 순서) {h}")
print("  검증:", verify_merkle_proof(txids[2], 2, proof, root))
print("  다른 위치로 속이면:", verify_merkle_proof(txids[2], 3, proof, root))
for n in (16, 1024, 4096):
    fake = [n.to_bytes(4, "big").hex() + k.to_bytes(28, "big").hex() for k in range(n)]
    print(f"  트랜잭션 {n:>5}개 → 증명 해시 {len(merkle_proof(fake, 0))}개")

print("== 3. 홀수 복제의 함정 ==")
a, b, c = txids[:3]
print("  [A, B, C]    ", merkle_root([a, b, c]))
print("  [A, B, C, C] ", merkle_root([a, b, c, c]))
