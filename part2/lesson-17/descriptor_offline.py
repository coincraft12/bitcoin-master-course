"""4-4 보충: 단일 키 디스크립터를 lib만으로 펼쳐 주소를 만든다 (Core의 deriveaddresses와 대조).

지원: pkh(KEY) · sh(wpkh(KEY)) · wpkh(KEY) · tr(KEY), KEY = [지문/경로]xpub|tpub/…/*
    python part2/lesson-17/descriptor_offline.py "$DESC" 0 4
인자가 없으면 공개된 테스트 니모닉의 m/84h/1h/0h 계정으로 예시 디스크립터를 만든다.
체크섬(# 뒤 8글자)은 여기서 검사하지 않는다 — Core의 getdescriptorinfo가 검사한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import re
from lib.ec import G, point_mul
from lib.keys import ser_compressed, p2pkh_address, p2sh_p2wpkh_address, p2wpkh_address, p2tr_address
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import parse_extended, derive_pub, derive_xpub, fingerprint, master
from lib.taproot import output_key


def parse_desc(desc: str):
    body = desc.split("#")[0]
    m = re.fullmatch(r"(pkh|wpkh|tr|sh\(wpkh)\((\[[^\]]*\])?([xt]pub\w+)((?:/\d+[hH']?)*)/\*\)\)?", body)
    if not m:
        raise ValueError("이 스크립트가 지원하지 않는 디스크립터 형식")
    return m.group(1), m.group(2), m.group(3), m.group(4).lstrip("/")


def addresses(desc: str, start: int, end: int):
    func, origin, ext, sub = parse_desc(desc)
    e = parse_extended(ext)
    testnet = e["testnet"]
    out = []
    for i in range(start, end + 1):
        K, _ = derive_pub(e["key"], e["chain_code"], f"{sub}/{i}" if sub else str(i))
        pub = ser_compressed(K)
        if func == "pkh":
            out.append(p2pkh_address(pub, 0x6f if testnet else 0x00))
        elif func == "sh(wpkh":
            out.append(p2sh_p2wpkh_address(pub, 0xc4 if testnet else 0x05))
        elif func == "wpkh":
            out.append(p2wpkh_address(pub, hrp="bcrt" if testnet else "bc"))
        else:
            out.append(p2tr_address(output_key(pub[1:]), hrp="bcrt" if testnet else "bc"))
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1:
        desc = sys.argv[1]
        start, end = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 4)
    else:
        seed = mnemonic_to_seed("abandon " * 11 + "about")          # 공개된 테스트 니모닉
        fp = fingerprint(point_mul(G, master(seed)[0])).hex()
        desc = f"wpkh([{fp}/84h/1h/0h]{derive_xpub(seed, 'm/84h/1h/0h', testnet=True)}/0/*)"
        start, end = 0, 4
        print("예시 디스크립터:", desc)
    for i, a in zip(range(start, end + 1), addresses(desc, start, end)):
        print(i, a)
