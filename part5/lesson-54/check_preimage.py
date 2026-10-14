"""13-2 실습 ③: 결제 영수증 확인 — SHA256(preimage) = payment_hash (s132-lab2, 13-1 HTLC).

    python part5/lesson-54/check_preimage.py <payment_preimage hex> <payment_hash hex>
    python part5/lesson-54/check_preimage.py          # 인자 없이: 원리 시연 (고정 preimage)

payment_hash는 alice의 `lncli decodepayreq <인보이스>`에서, payment_preimage는 결제 후
`lncli listpayments`(또는 payinvoice 출력)에서 얻는다. 노드 없이 실행된다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.hashes import sha256


def is_receipt(preimage: bytes, payment_hash: bytes) -> bool:
    """캐럴(받는 쪽)만 알던 R을 공개했다 = 결제가 끝났다는 증거."""
    return sha256(preimage) == payment_hash


if __name__ == "__main__":
    if len(sys.argv) == 3:
        r, h = bytes.fromhex(sys.argv[1]), bytes.fromhex(sys.argv[2])
    else:
        r = bytes(range(32))                          # 시연용 고정 preimage 00 01 … 1f
        h = sha256(r)
        print("시연: preimage = 00 01 02 … 1f (32바이트)")
    print("preimage     :", r.hex())
    print("SHA256       :", sha256(r).hex())
    print("payment_hash :", h.hex())
    print("일치         :", is_receipt(r, h))
    if not is_receipt(r, h):
        sys.exit(1)
