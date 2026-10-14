"""최종 프로젝트 풀이: Taproot 볼트 디스크립터 작성과 주소 계산 (s14-final 01·02).

설계 (6-2, 6-5, 7-4, 12-4)
    tr(키 경로, {multi_a(2,K1,K2,K3), and_v(v:pk(R),older(N))})
    키 경로 = 단일 키(소유자) 또는 musig(K1,K2) (2-of-2 MuSig2, Core 31부터 지갑 서명)
    리프 1 = 2-of-3 CHECKSIGADD, 리프 2 = 타임락 복구 (N블록 미사용 후 복구 키 R 단독)

이 파일은 노드 없이
  1) 디스크립터 문자열을 만들고 체크섬을 붙인다 (Bitcoin Core 테스트 프레임워크 descriptors.py 그대로 사용)
  2) 디스크립터에서 주소를 직접 계산한다 (키 파생 4-2 → 리프 스크립트 → TapLeaf/TapBranch → 출력키 6-4·6-5)
  3) 2)의 계산기를 BIP386·BIP387 공식 테스트 벡터(tr_vectors.json)로 자체 확인한다
Core가 만든 주소와 2)의 주소가 같으면 디스크립터를 제대로 이해한 것이다 (vault_wallet.sh가 대조한다).

    python part5/lesson-60/final_project/solution/vault_descriptor.py selftest
    python part5/lesson-60/final_project/solution/vault_descriptor.py demo
    python part5/lesson-60/final_project/solution/vault_descriptor.py build --keypath K0 --k1 K1 --k2 K2 --k3 K3 --rescue R --older 20 [--network regtest] [--count 3]
    python part5/lesson-60/final_project/solution/vault_descriptor.py address '<체크섬 붙은 디스크립터>' [--network regtest] [--count 3]

K는 "[지문/경로]tpub…" 형태(listdescriptors에서 뽑은 그대로). 받는용은 /0/*, 잔돈용은 /1/*를 이 스크립트가 붙인다.
musig() 키 경로는 디스크립터 문자열만 만든다(주소 계산은 BIP327·BIP328 집계가 필요해 Core에 맡긴다).
교육용 구현. 실제 자금에 쓰지 말 것.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import argparse
import json
import re
from lib.bip32 import parse_extended, ckd_priv, ckd_pub, HARD
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import derive_xpub, master, fingerprint
from lib.keys import public_key, parse_pubkey, parse_wif, ser_xonly, p2tr_address
from lib.taproot import tagged_hash, output_key
from descriptors import descsum_create, descsum_check      # Bitcoin Core test_framework (MIT)

HERE = pathlib.Path(__file__).resolve().parent
NUMS = "50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0"   # 6-5 NUMS 점
HRP = {"main": "bc", "signet": "tb", "testnet4": "tb", "regtest": "bcrt"}
OP_CHECKSIG, OP_CHECKSIGVERIFY, OP_CHECKSIGADD = 0xAC, 0xAD, 0xBA
OP_NUMEQUAL, OP_CHECKSEQUENCEVERIFY = 0x9C, 0xB2


# ---------- 디스크립터 문자열 만들기 ----------

def vault_descriptor(keypath: str, k1: str, k2: str, k3: str, rescue: str, older: int,
                     branch: int, musig: bool = False) -> str:
    """체크섬을 붙인 볼트 디스크립터. branch 0 = 받는용, 1 = 잔돈용."""
    if not 1 <= older <= 65535:
        raise ValueError("older는 1..65,535블록 (상대 타임락 상한, 6-3)")
    b = f"/{branch}/*"
    kp = f"musig({k1},{k2}){b}" if musig else f"{keypath}{b}"
    leaf_multi = f"multi_a(2,{k1}{b},{k2}{b},{k3}{b})"
    leaf_rescue = f"and_v(v:pk({rescue}{b}),older({older}))"
    return descsum_create(f"tr({kp},{{{leaf_multi},{leaf_rescue}}})")


# ---------- 디스크립터 → 스크립트 (필요한 조각만) ----------

def split_args(s: str) -> list:
    """맨 바깥 쉼표로 나눈다. (), [], {} 안의 쉼표는 건너뛴다."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def resolve_key(expr: str, index: int):
    """키 표현식 → 곡선 위의 점. [origin], 16진 공개키(32/33B), WIF, 확장 키/경로/* 지원."""
    expr = re.sub(r"^\[[^\]]*\]", "", expr)
    if re.fullmatch(r"[0-9a-fA-F]{64}", expr):
        return parse_pubkey(b"\x02" + bytes.fromhex(expr))
    if re.fullmatch(r"[0-9a-fA-F]{66}", expr):
        return parse_pubkey(bytes.fromhex(expr))
    parts = expr.split("/")
    if parts[0][1:4] in ("prv", "pub") and len(parts[0]) > 100:
        e = parse_extended(parts[0])
        key, c = e["key"], e["chain_code"]
        for p in parts[1:]:
            hard = p[-1] in "'h"
            p = p.rstrip("'h")
            i = (index if p == "*" else int(p)) + (HARD if hard else 0)
            if e["private"]:
                key, c = ckd_priv(key, c, i)
            else:
                key, c = ckd_pub(key, c, i)
        return public_key(key) if e["private"] else key
    d, _, _ = parse_wif(expr)
    return public_key(d)


def push(b: bytes) -> bytes:
    if len(b) > 75:
        raise ValueError("이 계산기는 75바이트 이하 푸시만 쓴다")
    return bytes([len(b)]) + b


def push_num(n: int) -> bytes:
    """CScriptNum 최소 인코딩 푸시. 1..16은 OP_1..OP_16."""
    if 1 <= n <= 16:
        return bytes([0x50 + n])
    out = n.to_bytes((n.bit_length() + 7) // 8, "little")
    if out[-1] & 0x80:
        out += b"\x00"
    return push(out)


def xonly(expr: str, index: int) -> bytes:
    return ser_xonly(resolve_key(expr, index))


def leaf_script(frag: str, index: int) -> bytes:
    """tapscript 조각 → 스크립트 바이트. pk, multi_a, sortedmulti_a, and_v(v:pk(K),older(N))."""
    m = re.fullmatch(r"pk\((.*)\)", frag)
    if m:
        return push(xonly(m.group(1), index)) + bytes([OP_CHECKSIG])
    m = re.fullmatch(r"(sorted)?multi_a\((.*)\)", frag)
    if m:
        args = split_args(m.group(2))
        k, keys = int(args[0]), [xonly(a, index) for a in args[1:]]
        if m.group(1):
            keys.sort()
        s = push(keys[0]) + bytes([OP_CHECKSIG])
        for key in keys[1:]:
            s += push(key) + bytes([OP_CHECKSIGADD])
        return s + push_num(k) + bytes([OP_NUMEQUAL])
    m = re.fullmatch(r"and_v\(v:pk\((.*)\),older\((\d+)\)\)", frag)
    if m:
        return push(xonly(m.group(1), index)) + bytes([OP_CHECKSIGVERIFY]) \
            + push_num(int(m.group(2))) + bytes([OP_CHECKSEQUENCEVERIFY])
    raise ValueError(f"이 계산기가 모르는 조각: {frag[:30]}")


def ser_compact(n: int) -> bytes:
    return bytes([n]) if n < 0xfd else b"\xfd" + n.to_bytes(2, "little")


def tapleaf_hash(script: bytes, leaf_version: int = 0xC0) -> bytes:       # 6-5 s65-code와 같은 계산
    return tagged_hash("TapLeaf", bytes([leaf_version]) + ser_compact(len(script)) + script)


def tapbranch_hash(a: bytes, b: bytes) -> bytes:
    return tagged_hash("TapBranch", min(a, b) + max(a, b))


def tree_root(tree: str, index: int, leaves: list) -> bytes:
    """{A,B} 중첩 트리의 머클 루트. leaves에 (리프 스크립트 hex, 깊이)를 모은다."""
    def walk(t, depth):
        if t.startswith("{"):
            a, b = split_args(t[1:-1])
            return tapbranch_hash(walk(a, depth + 1), walk(b, depth + 1))
        s = leaf_script(t, index)
        leaves.append((s.hex(), depth))
        return tapleaf_hash(s)
    return walk(tree, 0)


def tr_output(desc: str, index: int = 0) -> tuple:
    """tr() 디스크립터 → (scriptPubKey hex, 리프 목록)."""
    if "#" in desc:
        if not descsum_check(desc):
            raise ValueError("디스크립터 체크섬 불일치")
        desc = desc.split("#")[0]
    if not (desc.startswith("tr(") and desc.endswith(")")):
        raise ValueError("tr(...) 디스크립터만")
    args = split_args(desc[3:-1])
    if args[0].startswith("musig("):
        raise ValueError("musig() 키 경로의 주소는 Core로 확인한다 (BIP327 키 집계 필요)")
    internal = xonly(args[0], index)
    leaves = []
    root = tree_root(args[1], index, leaves) if len(args) > 1 else b""
    return "5120" + output_key(internal, root).hex(), leaves


def addresses(desc: str, network: str, count: int) -> list:
    return [p2tr_address(bytes.fromhex(tr_output(desc, i)[0][4:]), HRP[network]) for i in range(count)]


# ---------- 명령 ----------

def selftest() -> bool:
    data = json.load(open(HERE / "tr_vectors.json", encoding="utf-8"))
    ok = total = 0
    for v in data["vectors"]:
        for i, want in enumerate(v["scripts"]):
            total += 1
            got = tr_output(v["desc"], i)[0]
            ok += got == want
            if got != want:
                print(f"불일치 BIP{v['bip']} #{i}: {v['desc'][:50]}…")
    print(f"BIP386·BIP387 tr() 테스트 벡터 scriptPubKey {ok}/{total} 일치")
    return ok == total


def show(descs: list, network: str, count: int):
    for name, d in zip(("받는용 EXT", "잔돈용 INT"), descs):
        print(f"{name}: {d}")
    try:
        spk, leaves = tr_output(descs[0], 0)
    except ValueError as e:
        print(f"(주소 계산 생략: {e})")
        return
    print("리프 (깊이, 바이트, 스크립트 hex):")
    for h, depth in leaves:
        print(f"  {depth}  {len(h) // 2:>3}B  {h}")
    print(f"받는 주소 처음 {count}개 ({network}):")
    for i, a in enumerate(addresses(descs[0], network, count)):
        print(f"  /0/{i}  {a}")


def demo():
    """공개 테스트 니모닉(abandon ×11 + about)에서 키 5개를 파생해 디스크립터와 주소를 만든다 (결정적).
    실제 자금용이 아니다. 실제 프로젝트에서는 각 참여자 지갑의 tpub을 쓴다."""
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    names = ["소유자(키 경로)", "K1", "K2", "K3", "복구 R"]
    fp = fingerprint(public_key(master(seed)[0])).hex()
    keys = []
    for acct, n in enumerate(names):
        path = f"m/86h/1h/{acct}h"
        tpub = derive_xpub(seed, path, testnet=True)
        keys.append(f"[{fp}/86h/1h/{acct}h]{tpub}")
        print(f"{n:<14} {path}  {tpub[:20]}…")
    descs = [vault_descriptor(keys[0], keys[1], keys[2], keys[3], keys[4], 20, b) for b in (0, 1)]
    show(descs, "regtest", 2)


def main():
    ap = argparse.ArgumentParser(description="Taproot 볼트 디스크립터")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("demo")
    b = sub.add_parser("build")
    for k in ("keypath", "k1", "k2", "k3", "rescue"):
        b.add_argument(f"--{k}", required=(k != "keypath"))
    b.add_argument("--older", type=int, default=52560)
    b.add_argument("--musig", action="store_true", help="키 경로를 musig(K1,K2)로")
    b.add_argument("--network", default="regtest")
    b.add_argument("--count", type=int, default=3)
    b.add_argument("--quiet", action="store_true", help="디스크립터 두 줄만 출력 (스크립트용)")
    a = sub.add_parser("address")
    a.add_argument("desc")
    a.add_argument("--network", default="regtest")
    a.add_argument("--count", type=int, default=3)
    x = ap.parse_args()
    if x.cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    if x.cmd == "demo":
        demo()
    elif x.cmd == "build":
        if not x.musig and not x.keypath:
            ap.error("--keypath 또는 --musig 중 하나가 필요하다")
        descs = [vault_descriptor(x.keypath, x.k1, x.k2, x.k3, x.rescue, x.older, br, x.musig) for br in (0, 1)]
        if x.quiet:
            print("\n".join(descs))
        else:
            show(descs, x.network, x.count)
    elif x.cmd == "address":
        for addr in addresses(x.desc, x.network, x.count):
            print(addr)


if __name__ == "__main__":
    main()
