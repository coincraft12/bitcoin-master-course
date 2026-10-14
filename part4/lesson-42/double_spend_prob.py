"""10-3 확인 수와 이중지불 확률 — 백서 11절 계산식으로 표 재계산 (노드 없이 실행).

공격자 해시 비율 q, 정직한 쪽 p = 1 − q, 확인 수 z일 때 공격자가 따라잡을 확률(백서 11절):
    λ = z · q / p
    P = 1 − Σ_{k=0..z} (λ^k e^{−λ} / k!) · (1 − (q/p)^(z−k))
P < 0.1%가 되는 최소 z를 찾는다.

    python part4/lesson-42/double_spend_prob.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import math
from lib.block import block_work


def attacker_success(q: float, z: int) -> float:
    p = 1.0 - q
    lam = z * (q / p)
    total = 1.0
    for k in range(z + 1):
        poisson = math.exp(-lam)
        for i in range(1, k + 1):
            poisson *= lam / i
        total -= poisson * (1 - (q / p) ** (z - k))
    return total


def confirmations_needed(q: float, limit: float = 0.001) -> int:
    z = 0
    while attacker_success(q, z) >= limit:
        z += 1
    return z


print("공격자 해시 비율 | 성공 확률 0.1% 미만이 되는 확인 수")
for q in (0.10, 0.15, 0.20, 0.25, 0.30):
    print(f"{q:>14.0%} | {confirmations_needed(q):>3}")
print("q = 10%, z = 0..6:", " ".join(f"{attacker_success(0.1, z):.7f}" for z in range(7)))

print("== 가장 긴 체인이 아니라 가장 무거운 체인 (block_work = 2^256 ÷ (타깃 + 1)) ==")
easy = 10 * block_work(0x207fffff)       # regtest 난이도 블록 10개
hard = 1 * block_work(0x1d00ffff)        # 메인넷 난이도 1 블록 1개
print(f"regtest 난이도 블록 10개 작업량 {easy} · 난이도 1 블록 1개 작업량 {hard} → 무거운 쪽: {'짧은 체인' if hard > easy else '긴 체인'}")
