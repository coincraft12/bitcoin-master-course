"""2부 미니 과제 01 정답: BIP84·BIP86 첫 주소 3개씩과 Core용 디스크립터.

먼저 mainnet 경로로 BIP84·BIP86 공식 테스트 벡터와 맞는지 스스로 확인한 뒤 regtest 값을 출력한다.

    python part2/lesson-18/assignment/solution/solution_recovery_kit.py "<테스트 니모닉>"
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from lib.ec import G, point_mul
from lib.keys import ser_compressed, p2wpkh_address, p2tr_address
from lib.bip39 import is_valid, mnemonic_to_seed
from lib.bip32 import master, serialize, derive_priv
from lib.taproot import output_key

TEST_MNEMONIC = "abandon " * 11 + "about"


def _pubs(mnemonic: str, purpose: int, n: int, regtest: bool):
    seed = mnemonic_to_seed(mnemonic)
    coin = "1h" if regtest else "0h"
    for i in range(n):
        k, _ = derive_priv(seed, f"m/{purpose}h/{coin}/0h/0/{i}")
        yield ser_compressed(point_mul(G, k))


def bip84_addresses(mnemonic: str, n: int = 3, regtest: bool = True) -> list:
    hrp = "bcrt" if regtest else "bc"
    return [p2wpkh_address(pub, hrp=hrp) for pub in _pubs(mnemonic, 84, n, regtest)]


def bip86_addresses(mnemonic: str, n: int = 3, regtest: bool = True) -> list:
    hrp = "bcrt" if regtest else "bc"
    return [p2tr_address(output_key(pub[1:]), hrp=hrp) for pub in _pubs(mnemonic, 86, n, regtest)]


def core_descriptors(mnemonic: str, purpose: int) -> tuple:
    k, c = master(mnemonic_to_seed(mnemonic))
    tprv = serialize(k, c, testnet=True)
    func = {84: "wpkh", 86: "tr"}[purpose]
    return tuple(f"{func}({tprv}/{purpose}h/1h/0h/{chain}/*)" for chain in (0, 1))


def self_check():
    """mainnet 경로 결과를 BIP 문서의 공식 벡터와 대조."""
    root = pathlib.Path(__file__).resolve().parents[4]
    import json
    dv = json.load(open(root / "data" / "bip_derivation_vectors.json", encoding="utf-8"))
    want84 = [a["address"] for a in dv["bip84"]["addresses"] if a["path"].split("/")[-2] == "0"]
    want86 = [a["address"] for a in dv["bip86"]["addresses"] if a["path"].split("/")[-2] == "0"]
    ok84 = bip84_addresses(TEST_MNEMONIC, len(want84), regtest=False) == want84
    ok86 = bip86_addresses(TEST_MNEMONIC, len(want86), regtest=False) == want86
    print(f"자체 확인 (공식 벡터 BIP84 {len(want84)}개, BIP86 {len(want86)}개): {ok84 and ok86}")


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else TEST_MNEMONIC
    if not is_valid(m):
        sys.exit("니모닉 체크섬이 맞지 않습니다.")
    self_check()
    print("BIP84 (regtest, m/84h/1h/0h/0/0..2):", *bip84_addresses(m), sep="\n  ")
    print("BIP86 (regtest, m/86h/1h/0h/0/0..2):", *bip86_addresses(m), sep="\n  ")
    for p in (84, 86):
        r, c = core_descriptors(m, p)
        print(f"RECV{p}=\"{r}\"\nCHG{p}=\"{c}\"")
