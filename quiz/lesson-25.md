# lesson-25 퀴즈 · 6-3 타임락: nLockTime, nSequence, CLTV, CSV 실습

출처: s63-quiz 슬라이드와 나레이션.

## Q1. 출력 자체를 특정 높이까지 잠그는 방법은?

- **A** nLockTime만 설정
- **B** 잠금 스크립트에 CLTV
- **C** nSequence를 0xffffffff로
- **D** version을 1로

<details><summary>정답</summary>

**B**

출력 자체를 특정 높이까지 잠그는 방법은 B, 잠금 스크립트에 CHECKLOCKTIMEVERIFY를 넣는 것입니다. nLockTime만 설정하면 그 트랜잭션에만 적용되므로 A는 틀렸고, nSequence를 0xffffffff로 두면 오히려 nLockTime이 무시됩니다.

</details>

## Q2. nLockTime 값 800,000의 의미는?

- **A** 유닉스 시간
- **B** 블록 높이
- **C** 블록 수
- **D** 초 단위 지연

<details><summary>정답</summary>

**B** — 5억 미만 = 높이

nLockTime 값 800,000은 B, 블록 높이입니다. 5억 미만이므로 높이로 해석합니다.

</details>

## Q3. 실습 3단계 (b)가 거부된 이유는?

- **A** 서명 오류
- **B** 수수료 부족
- **C** 아직 그 높이에 도달하지 않음
- **D** 더스트 출력

<details><summary>정답</summary>

**C** — non-final

실습 3단계 b가 거부된 이유는 C, 아직 그 높이에 도달하지 않았기 때문입니다. 트랜잭션 자체가 아직 최종 상태가 아닌 non-final입니다. 서명은 정상적으로 완료되었으므로 A는 아니고, 수수료나 더스트 문제도 아닙니다.

</details>
