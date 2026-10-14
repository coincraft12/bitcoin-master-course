"""10-2 gettxoutproof 결과 해석 (선택 과제: 형제 해시를 꺼내 루트 재계산).

    python part4/lesson-41/txoutproof.py <PROOF hex>          # proof_lab.sh가 호출
    python part4/lesson-41/txoutproof.py --demo               # 블록 100,000으로 만든 증명 (노드 없이)

PROOF = 헤더 80바이트 + 트랜잭션 수 + 해시 목록 + 플래그 비트 (BIP37 merkleblock 형식).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
from lib.block import parse_header, parse_merkleblock, extract_matches, build_merkleblock


def explain(proof_hex: str):
    pmt = parse_merkleblock(proof_hex)
    hdr = parse_header(pmt["header"])
    print("앞 80바이트 = 블록 헤더 → 해시", hdr["hash"])
    print("블록의 트랜잭션 수", pmt["n_tx"], "· 증명 해시", len(pmt["hashes"]), "개 · 플래그 비트",
          "".join("1" if x else "0" for x in pmt["bits"]))
    for h in pmt["hashes"]:
        print("  해시(표시 순서)", h[::-1].hex())
    root, matches = extract_matches(pmt)
    print("재계산한 루트", root)
    print("헤더의 루트  ", hdr["merkle_root"], "→", "일치" if root == hdr["merkle_root"] else "불일치")
    for pos, txid in matches:
        print(f"증명된 트랜잭션: 위치 {pos}, txid {txid}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--demo"]:
        B = json.load(open(pathlib.Path(__file__).resolve().parents[2] / "data" / "block100000.json", encoding="utf-8"))
        explain(build_merkleblock(bytes.fromhex(B["header"]), B["txids"], {B["txids"][2]}))
    else:
        if len(sys.argv) != 2:
            sys.exit("사용법: python part4/lesson-41/txoutproof.py <PROOF hex>  또는  --demo")
        explain(sys.argv[1])
