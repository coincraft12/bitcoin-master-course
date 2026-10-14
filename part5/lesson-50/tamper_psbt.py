"""12-2 심화: 받는 주소를 바꾼 PSBT 만들기 (s122-lab 심화, 5-4 심화와 같은 실험).

온라인 측이 해킹당했다고 가정한다. 공격자는 입력·금액·잔돈은 그대로 두고
받는 출력의 주소만 자기 주소로 바꾼 PSBT를 서명기에 넘긴다.
→ 서명 단계 전에 check_psbt.py(체크리스트 1번)가 잡아내야 한다.

    python part5/lesson-50/tamper_psbt.py /tmp/unsigned.psbt <공격자 주소> /tmp/tampered.psbt

같은 입력·sequence·금액으로 createpsbt를 다시 만들고, 감시 지갑(watch)의
walletprocesspsbt(sign=false)로 서명에 필요한 정보(witness_utxo, 파생 경로)를 채운다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.rpc import RPC


def tampered_outputs(dec: dict, attacker: str) -> list:
    """파생 경로가 없는 출력(=잔돈이 아닌 받는 출력)의 주소를 attacker로 바꾼 createpsbt 출력 목록.
    금액은 문자열로 넘긴다(JSON에 float를 쓰지 않는다)."""
    outs = []
    for v, o in zip(dec["tx"]["vout"], dec["outputs"]):
        is_change = bool(o.get("bip32_derivs") or o.get("taproot_bip32_derivs"))
        addr = v["scriptPubKey"]["address"] if is_change else attacker
        outs.append({addr: f"{v['value']:.8f}"})
    return outs


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    src, attacker, dst = sys.argv[1:]
    node, watch = RPC(), RPC(wallet="watch")
    dec = node.decodepsbt(pathlib.Path(src).read_text(encoding="utf-8").strip())
    ins = [{"txid": i["txid"], "vout": i["vout"], "sequence": i["sequence"]} for i in dec["tx"]["vin"]]
    raw = node.createpsbt(ins, tampered_outputs(dec, attacker), dec["tx"]["locktime"])
    filled = watch.walletprocesspsbt(raw, False)["psbt"]
    pathlib.Path(dst).write_text(filled + "\n", encoding="utf-8")
    print(f"받는 주소를 {attacker} 로 바꾼 PSBT → {dst}")
    print("이제 check_psbt.py로 확인해 보라. 1번 항목에서 실패해야 정상이다.")


if __name__ == "__main__":
    main()
