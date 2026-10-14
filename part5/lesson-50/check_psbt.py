"""12-2 서명 전 확인 체크리스트 5개를 decodepsbt 출력에서 하나씩 (s122-check, s122-lab).

오프라인 측(서명기 자리)에서 서명하기 전에 돌린다. 하드웨어 지갑이 화면에 보여 주는 것을
스크립트로 흉내 낸 것이다. 하나라도 실패하면 종료 코드 1 → 서명하지 않는다.

    python part5/lesson-50/check_psbt.py /tmp/unsigned.psbt <받는 사람이 알려 준 주소> 0.1
    python part5/lesson-50/check_psbt.py /tmp/unsigned.psbt <주소> 0.1 --signer signer --max-feerate 50

  1 받는 주소가 의도한 주소와 전체 일치하는가 (12-1 주소 중독)
  2 금액이 맞는가
  3 수수료가 상식적인가: 입력 금액 합 − 출력 합 = fee (7-4), 수수료율 상한
  4 잔돈 출력이 내 지갑 주소인가: outputs[].bip32_derivs + 서명 지갑 getaddressinfo
  5 스크립트(멀티시그 등) 입력이면 서명 지갑이 그 디스크립터를 알고 있는가 (등록 안 하면 잔돈 검증 불가)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import argparse
from decimal import Decimal
from lib.rpc import RPC, btc_to_sat


def fmt_rate(fee_sat: int, vsize: int) -> str:
    """수수료율을 소수 첫째 자리까지 (float 없이)."""
    q = fee_sat * 10 // vsize
    return f"{q // 10}.{q % 10} sat/vB"


def run_checks(dec: dict, intended: str, amount_sat: int, ismine, max_feerate: int = 50) -> list:
    """decodepsbt 결과 dec로 체크리스트를 돌려 [(통과 여부, 항목 번호, 설명)]을 돌려준다.
    ismine(address) -> bool 은 서명 지갑이 그 주소를 자기 것으로 아는지 알려 주는 함수."""
    res = []
    vouts = dec["tx"]["vout"]
    outs = dec.get("outputs", [{}] * len(vouts))
    addrs = [v["scriptPubKey"].get("address") for v in vouts]

    # 1. 받는 주소 전체 일치
    pay = [i for i, a in enumerate(addrs) if a == intended]
    if pay:
        res.append((True, 1, f"받는 주소 전체 일치: vout {pay[0]} = {intended}"))
    else:
        res.append((False, 1, f"의도한 주소 {intended} 로 가는 출력이 없다. 출력 주소: {addrs}"))

    # 2. 금액
    if pay:
        got = btc_to_sat(str(vouts[pay[0]]["value"]))
        res.append((got == amount_sat, 2, f"금액 {got:,} sat (의도 {amount_sat:,} sat)"))
    else:
        res.append((False, 2, "받는 출력이 없어 금액을 확인할 수 없다"))

    # 3. 수수료: 입력 금액은 witness_utxo(또는 non_witness_utxo)에서. 없으면 서명기가 수수료를 모른다.
    in_sat = 0
    missing = []
    for i, (txin, pin) in enumerate(zip(dec["tx"]["vin"], dec["inputs"])):
        if "witness_utxo" in pin:
            in_sat += btc_to_sat(str(pin["witness_utxo"]["amount"]))
        elif "non_witness_utxo" in pin:
            in_sat += btc_to_sat(str(pin["non_witness_utxo"]["vout"][txin["vout"]]["value"]))
        else:
            missing.append(i)
    out_sat = sum(btc_to_sat(str(v["value"])) for v in vouts)
    if missing:
        res.append((False, 3, f"입력 {missing}의 이전 출력 금액이 PSBT에 없다 → 수수료를 검증할 수 없다"))
    else:
        fee = in_sat - out_sat
        vsize = dec["tx"]["vsize"]
        ok = 0 < fee <= max_feerate * vsize and fee < amount_sat
        msg = f"입력 {in_sat:,} − 출력 {out_sat:,} = 수수료 {fee:,} sat, {fmt_rate(fee, vsize)} (상한 {max_feerate} sat/vB)"
        if "fee" in dec and btc_to_sat(str(dec["fee"])) != fee:
            ok = False
            msg += f" · decodepsbt fee {dec['fee']} 와 다르다"
        res.append((ok, 3, msg))

    # 4. 잔돈: 받는 출력이 아닌 출력은 모두 내 지갑 것이어야 한다
    for i, (a, o) in enumerate(zip(addrs, outs)):
        if i in pay:
            continue
        derivs = o.get("bip32_derivs") or o.get("taproot_bip32_derivs")
        mine = bool(a) and ismine(a)
        res.append((bool(derivs) and mine, 4,
                    f"vout {i} {a}: 파생 경로 {'있음' if derivs else '없음'}, 서명 지갑 소유 {'예' if mine else '아니오'}"))

    # 5. 스크립트 입력(멀티시그·miniscript·tapscript)이면 디스크립터 등록 여부
    scripted = [i for i, p in enumerate(dec["inputs"]) if "witness_script" in p or "taproot_scripts" in p]
    if not scripted:
        res.append((True, 5, "단일 서명 입력 — 해당 없음"))
    else:
        change = [a for i, a in enumerate(addrs) if i not in pay and a]
        known = all(ismine(a) for a in change) if change else True
        res.append((known, 5, f"스크립트 입력 {scripted}: 잔돈 주소를 서명 지갑이 {'알아본다' if known else '모른다 → 디스크립터 등록 필요'}"))
    return res


def main():
    ap = argparse.ArgumentParser(description="서명 전 PSBT 확인 체크리스트")
    ap.add_argument("psbt_file")
    ap.add_argument("intended_address")
    ap.add_argument("amount_btc", help="예: 0.1 (문자열로 받아 Decimal로 바꾼다)")
    ap.add_argument("--signer", default="signer", help="서명 지갑 이름 (기본 signer)")
    ap.add_argument("--max-feerate", type=int, default=50, help="수수료율 상한 sat/vB (기본 50)")
    ap.add_argument("--network", default="regtest")
    a = ap.parse_args()

    psbt = pathlib.Path(a.psbt_file).read_text().strip()
    node = RPC(a.network)
    signer = RPC(a.network, wallet=a.signer)
    dec = node.decodepsbt(psbt)

    def ismine(addr):
        return bool(signer.getaddressinfo(addr).get("ismine"))

    results = run_checks(dec, a.intended_address, btc_to_sat(Decimal(a.amount_btc)), ismine, a.max_feerate)
    for ok, n, msg in results:
        print(f"[{'통과' if ok else '실패'}] {n}. {msg}")
    if all(ok for ok, _, _ in results):
        print("→ 5개 항목 통과. 서명해도 좋다.")
    else:
        print("→ 서명하지 않는다. 온라인 측과 받는 사람에게 다른 경로로 확인한다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
