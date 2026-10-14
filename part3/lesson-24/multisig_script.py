"""6-2 노드 없이: 2-of-3 잠금 스크립트(sortedmulti)를 직접 만들고 P2SH·P2WSH 주소와 해제 witness 모양을 본다.

공개된 테스트 니모닉(abandon ×11 + about)의 m/84h/1h/{0,1,2}h/0/0 공개키 셋 · 실제 자금에 쓰지 말 것.
실행: python part3/lesson-24/multisig_script.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, point_mul
from lib.keys import ser_compressed, p2sh_address, p2wsh_address
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_priv
from lib.hashes import hash160, sha256

NAMES = {0x00: "OP_0", 0x52: "OP_2", 0x53: "OP_3", 0xae: "OP_CHECKMULTISIG"}
seed = mnemonic_to_seed("abandon " * 11 + "about")
pubs = [ser_compressed(point_mul(G, derive_priv(seed, f"m/84h/1h/{a}h/0/0")[0])) for a in range(3)]


def multisig(m: int, keys: list) -> bytes:
    """OP_m <키>… OP_n OP_CHECKMULTISIG. sortedmulti는 키를 사전순 정렬 → 누가 만들어도 같은 주소."""
    s = bytes([0x50 + m])
    for k in keys:
        s += bytes([len(k)]) + k
    return s + bytes([0x50 + len(keys), 0xae])


def asm(script: bytes) -> str:
    out, i = [], 0
    while i < len(script):
        op = script[i]; i += 1
        if 0x01 <= op <= 0x4b:
            out.append(script[i:i + op].hex()[:8] + "…"); i += op
        else:
            out.append(NAMES.get(op, hex(op)))
    return " ".join(out)


ws = multisig(2, sorted(pubs))
print("공개키 A·B·C (참여자 순서):", [p.hex()[:10] + "…" for p in pubs])
print("sortedmulti 순서         :", [p.hex()[:10] + "…" for p in sorted(pubs)])
print("witness script", len(ws), "B:", asm(ws))
print("P2SH  (HASH160, 20B):", hash160(ws).hex(), "→", p2sh_address(ws, version=0xc4))
print("P2WSH (SHA256, 32B) :", sha256(ws).hex(), "→", p2wsh_address(ws, hrp="bcrt"))
print("키 순서를 바꿔 만든 multi()   :", p2wsh_address(multisig(2, pubs[::-1]), hrp="bcrt"), "← 다른 주소")
print("\n해제 witness 모양 (서명 A, C): [빈 값(NULLDUMMY), <서명A>, <서명C>, witness script]")
print("서명 순서는 공개키 순서와 같아야 한다. CHECKMULTISIG는 키 목록을 앞에서부터 한 번만 훑는다.")
