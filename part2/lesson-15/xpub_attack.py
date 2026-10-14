"""4-2 실습: 계정 xpub + 일반 파생 자식 개인키 하나 → 부모 개인키 복원 (s42-attack, s42-code2).

공개된 테스트 니모닉만 쓴다. 교육용 시연.
실행: python part2/lesson-15/xpub_attack.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.ec import G, N, point_mul
from lib.keys import ser_compressed
from lib.bip39 import mnemonic_to_seed
from lib.bip32 import HARD, hmac512, ckd_priv, derive_priv

seed = mnemonic_to_seed("abandon " * 11 + "about")


# 공격 시연: 계정 xpub(K, c) + 자식 개인키 하나 → 부모 개인키
def recover_parent(K_parent, c_parent, k_child, i):
    I = hmac512(c_parent, ser_compressed(K_parent) + i.to_bytes(4, "big"))
    return (k_child - int.from_bytes(I[:32], "big")) % N


k_par, c_par = derive_priv(seed, "m/84h/1h/0h"); K_par = point_mul(G, k_par)
k_child, _ = ckd_priv(k_par, c_par, 5)
print(recover_parent(K_par, c_par, k_child, 5) == k_par)      # True

# 같은 실험을 강화 번호 5h로: I = HMAC(c, 0x00 ‖ 부모 개인키 ‖ i) 이므로
# 부모 개인키 없이는 I를 계산할 수 없다. 공개키를 넣어 억지로 계산하면 틀린 값이 나온다.
k_child_h, _ = ckd_priv(k_par, c_par, HARD + 5)
print(recover_parent(K_par, c_par, k_child_h, HARD + 5) == k_par)   # False
