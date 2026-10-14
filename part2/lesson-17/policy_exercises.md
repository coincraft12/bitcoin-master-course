# 4-4 실습 ⑤ · 말을 정책으로 옮겨 보기

먼저 스스로 써 본 뒤 아래 정답과 비교합니다. 정답 정책은 정책 컴파일러 도구(예: https://bitcoin.sipa.be/miniscript/ 의 Policy to Miniscript compiler)에 넣어 miniscript로 바꿔 확인합니다.

| 조건 (말) | 정책 (정답) |
|---|---|
| A와 B 둘 다 서명 | `and(pk(A),pk(B))` |
| 셋 중 둘 서명 | `thresh(2,pk(A),pk(B),pk(C))` |
| A 서명, 또는 1년(약 52,560블록) 뒤 B 서명 | `or(pk(A),and(pk(B),older(52560)))` |

## 확인할 점

- 1년 ≈ 365일 × 144블록 = 52,560블록.
- `older(n)`은 상대 타임락(BIP68)이며 블록 단위 상한은 65,535블록입니다. 52,560은 상한 안입니다. 상한을 넘는 값을 적으면 의도한 대로 동작하지 않습니다.
- 세 번째 정책은 12-4 상속 설계에서 다시 씁니다.

## 슬라이드 예시 (s44-mini2) — 정책 → miniscript → 디스크립터

```
POLICY      or(pk(A), and(pk(B), older(144)))
MINISCRIPT  or_d(pk(A),and_v(v:pk(B),older(144)))
DESCRIPTOR  wsh(or_d(pk(A),and_v(v:pk(B),older(144))))
```

"평소엔 A 혼자, A가 사라지면 하루(144블록) 뒤 B". Core는 `wsh()` 안 miniscript를 v25부터, `tr()` 안은 v26부터 감시·서명합니다. 6-3 타임락 실습이 이 형식을 씁니다.
