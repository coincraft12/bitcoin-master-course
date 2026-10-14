"""4-2 실습: BIP32 공식 테스트 벡터 1로 검증 (s42-code2 상단).

실행: python part2/lesson-15/bip32_vectors.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, point_mul
from lib.bip32 import master, fingerprint, derive_ext, serialize

seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
EXPECTED = {
    "m": "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi",
    "m/0h": "xprv9uHRZZhk6KAJC1avXpDAp4MDc3sQKNxDiPvvkX8Br5ngLNv1TxvUxt4cV1rGL5hj6KCesnDYUhd7oWgT11eZG7XnxHrnYeSvkzY7d2bhkJ7",
}
k, c = master(seed)
print("마스터 지문:", fingerprint(point_mul(G, k)).hex())
for path, want in EXPECTED.items():
    # derive_priv를 확장한 derive_ext: 깊이·부모 지문·자식 번호까지 돌려준다
    k, c, depth, parent_fp, child = derive_ext(seed, path)
    got = serialize(k, c, depth, parent_fp, child)
    print(f"{path:5} {'OK ' if got == want else 'FAIL'} {got}")
    print(f"      깊이 {depth}, 부모 지문 {parent_fp.hex()}, 자식 번호 {child:#010x}")
    print(f"      xpub {serialize(point_mul(G, k), c, depth, parent_fp, child)}")
