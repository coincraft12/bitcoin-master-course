"""6-5 LAB ④ (s65-code): 스크립트 경로 약속을 직접 검증.

    python part3/lesson-27/verify_commitment.py                       # 노드 없이: NUMS 아래 pk(B)·pk(C) 두 잎 예제
    python part3/lesson-27/verify_commitment.py <scriptPubKey hex> <리프 스크립트 hex> <컨트롤 블록 hex>
      → 지출된 출력의 scriptPubKey(5120…)와 witness 두 번째·세 번째 항목 (tapscript_lab.sh가 넘겨 준다)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.taproot import (verify_script_path, tapleaf_hash, tapbranch_hash, NUMS_H, taproot_tree, tweak_pubkey,
                         control_block, p2tr_script_pubkey)
from lib.keys import p2tr_address


def check(spk: bytes, script: bytes, control: bytes):
    out_key = spk[2:]                                    # 앞 0x51 0x20 제외한 출력키 32B
    print("리프 스크립트", len(script), "B:", script.hex())
    print("컨트롤 블록  ", len(control), "B: 버전·패리티", hex(control[0]), "· 내부키", control[1:33].hex()[:16] + "…",
          "· 형제 해시", [control[i:i+32].hex()[:16] + "…" for i in range(33, len(control), 32)])
    print("verify_script_path:", verify_script_path(out_key, script, control))
    print("컨트롤 블록의 내부키 = NUMS:", control[1:33] == NUMS_H)


if len(sys.argv) == 4:
    check(*(bytes.fromhex(a) for a in sys.argv[1:]))
else:
    from lib.ec import G, point_mul
    from lib.bip39 import mnemonic_to_seed
    from lib.bip32 import derive_priv
    seed = mnemonic_to_seed("abandon " * 11 + "about")          # 공개 테스트 니모닉 · 실제 자금 금지
    B, C = (point_mul(G, derive_priv(seed, f"m/86h/1h/{a}h/0/0")[0])[0].to_bytes(32, "big") for a in (1, 2))
    leaf = lambda x: (b"\x20" + x + b"\xac", 0xc0)              # pk(X) = <X> OP_CHECKSIG, 34바이트
    leaves, root = taproot_tree([leaf(B), leaf(C)])              # {pk(B), pk(C)}
    parity, Q = tweak_pubkey(NUMS_H, root)
    print("잎 해시 B", tapleaf_hash(*leaf(B)).hex())
    print("잎 해시 C", tapleaf_hash(*leaf(C)).hex())
    print("머클 루트", root.hex(), "= TapBranch(작은 쪽‖큰 쪽)", root == tapbranch_hash(tapleaf_hash(*leaf(B)), tapleaf_hash(*leaf(C))))
    print("출력키 Q ", Q.hex(), "· 주소", p2tr_address(Q, hrp="bcrt"))
    lv, script, path = leaves[1]                                 # C 리프로 지출
    print("\n-- C 리프로 지출할 때 witness: [C의 서명 64B, 리프 스크립트, 컨트롤 블록] --")
    check(p2tr_script_pubkey(Q), script, control_block(NUMS_H, lv, path, root))
    print("B 리프의 내용(B의 키)은 어디에도 없고 해시 32바이트로만 남는다.")
