"""4-5 실습: 니모닉에서 Core 지갑 복구용 정보 만들기 (s45-lab1, s45-lab2).

4-1(lib/bip39.py)과 4-2(lib/bip32.py)를 재사용한다. regtest 전용 테스트 니모닉만 쓴다.

    python part2/lesson-18/recover.py new
        새 테스트 니모닉, 마스터 tprv, m/84h/1h/0h/0/0 첫 주소(bcrt1q…), 디스크립터 두 줄(RECV, CHG)
    python part2/lesson-18/recover.py show "<니모닉>" [--passphrase 문구] [--purpose 84|44|49|86]
        같은 정보를 기존 니모닉에서 다시 계산 (실패 실험: --purpose 44, --passphrase …)

디스크립터 체크섬은 getdescriptorinfo로 받아 뒤에 #xxxxxxxx로 붙인다.
출력의 tprv는 비밀 정보다. regtest가 아닌 곳에 쓰지 말 것.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import argparse
from lib.ec import G, point_mul
from lib.keys import ser_compressed, p2pkh_address, p2sh_p2wpkh_address, p2wpkh_address, p2tr_address
from lib.bip39 import new_mnemonic, is_valid, mnemonic_to_seed
from lib.bip32 import master, serialize, derive_priv
from lib.taproot import output_key

# purpose → (디스크립터 함수 앞, 뒤, 주소 함수)
FUNCS = {
    84: ("wpkh(", ")", lambda pub: p2wpkh_address(pub, hrp="bcrt")),
    44: ("pkh(", ")", lambda pub: p2pkh_address(pub, 0x6f)),
    49: ("sh(wpkh(", "))", lambda pub: p2sh_p2wpkh_address(pub, 0xc4)),
    86: ("tr(", ")", lambda pub: p2tr_address(output_key(pub[1:]), hrp="bcrt")),
}


def recovery_info(mnemonic: str, passphrase: str = "", purpose: int = 84) -> dict:
    seed = mnemonic_to_seed(mnemonic, passphrase)
    k, c = master(seed)
    tprv = serialize(k, c, testnet=True)                       # 마스터 확장 개인키 (regtest)
    head, tail, addr = FUNCS[purpose]
    account = f"{purpose}h/1h/0h"                             # coin_type 1h = testnet·regtest
    first_pub = ser_compressed(point_mul(G, derive_priv(seed, f"m/{account}/0/0")[0]))
    return {
        "mnemonic": mnemonic,
        "tprv": tprv,
        "first_address": addr(first_pub),
        "RECV": f"{head}{tprv}/{account}/0/*{tail}",
        "CHG": f"{head}{tprv}/{account}/1/*{tail}",
    }


def main():
    ap = argparse.ArgumentParser(description="니모닉 → Core 디스크립터 복구 정보 (regtest)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new", help="새 테스트 니모닉 생성")
    show = sub.add_parser("show", help="기존 니모닉에서 다시 계산")
    show.add_argument("mnemonic")
    show.add_argument("--passphrase", default="")
    show.add_argument("--purpose", type=int, choices=sorted(FUNCS), default=84)
    a = ap.parse_args()
    if a.cmd == "new":
        info = recovery_info(new_mnemonic(12))
    else:
        if not is_valid(a.mnemonic):
            sys.exit("니모닉 체크섬이 맞지 않습니다. 철자와 단어 순서를 확인하세요.")
        info = recovery_info(a.mnemonic, a.passphrase, a.purpose)
    print("니모닉   :", info["mnemonic"])
    print("tprv     :", info["tprv"])
    print("첫 주소  :", info["first_address"])
    print(f"RECV=\"{info['RECV']}\"")
    print(f"CHG=\"{info['CHG']}\"")


if __name__ == "__main__":
    main()
