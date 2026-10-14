"""최종 프로젝트 과제 01·02: 볼트 디스크립터와 복구 리프 스크립트 (s14-final).

빈 함수 두 개를 채운다. 정답은 ../solution/vault_descriptor.py.
채운 뒤 실행하면 공개 테스트 니모닉(abandon ×11 + about)에서 만든 키로 풀이와 대조한다.

    python part5/lesson-60/final_project/exercise/exercise_vault_descriptor.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "solution"))   # 체크섬 도구·대조용
from descriptors import descsum_create          # noqa: F401  (풀이에 쓴다: Core 체크섬)


def vault_descriptor(keypath: str, k1: str, k2: str, k3: str, rescue: str, older: int, branch: int) -> str:
    """체크섬을 붙인 tr() 디스크립터.
    키 경로 = keypath/branch/*, 스크립트 트리 = {2-of-3 CHECKSIGADD 리프, 복구 키 + older(N) 리프}.
    힌트: multi_a, and_v(v:pk(…),older(…)), 트리는 중괄호 {A,B}. 6-5 s65-lab1, 12-4 s124-lab1 문법."""
    raise NotImplementedError("과제: tr(키경로,{multi_a(2,…),and_v(v:pk(…),older(N))}) 문자열 + descsum_create")


def rescue_leaf(rescue_xonly: bytes, older: int) -> bytes:
    """복구 리프 and_v(v:pk(R),older(N))의 tapscript 바이트.
    <R 32바이트 푸시> OP_CHECKSIGVERIFY <N 최소 인코딩> OP_CHECKSEQUENCEVERIFY  (N ≤ 16이면 OP_N)"""
    raise NotImplementedError("과제: 0x20 + R + 0xad + N 푸시 + 0xb2")


if __name__ == "__main__":
    import vault_descriptor as sol
    from lib.bip39 import mnemonic_to_seed
    from lib.bip32 import derive_xpub, master, fingerprint
    from lib.keys import public_key
    seed = mnemonic_to_seed("abandon " * 11 + "about")
    fp = fingerprint(public_key(master(seed)[0])).hex()
    keys = [f"[{fp}/86h/1h/{i}h]{derive_xpub(seed, f'm/86h/1h/{i}h', testnet=True)}" for i in range(5)]
    mine = vault_descriptor(*keys, 20, 0)
    want = sol.vault_descriptor(*keys, 20, 0)
    print("디스크립터 일치:", mine == want)
    R0 = sol.xonly(keys[4] + "/0/*", 0)
    for n in (5, 20, 52560):
        got = rescue_leaf(R0, n)
        ref = sol.leaf_script(f"and_v(v:pk({keys[4]}/0/*),older({n}))", 0)
        print(f"복구 리프 older({n}) 일치:", got == ref, got.hex()[-12:])
    print("첫 주소:", sol.addresses(mine, "regtest", 1)[0])
