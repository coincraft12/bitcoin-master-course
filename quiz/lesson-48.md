# lesson-48 퀴즈 · 11-5 소프트포크 활성화, 4부 미니 과제

출처: s115-quiz 슬라이드와 나레이션.

## Q1. BIP9 상태 중 새 규칙이 강제되기 시작하는 상태는?

- **A** STARTED
- **B** LOCKED_IN
- **C** ACTIVE
- **D** DEFINED

<details><summary>정답</summary>

**C**

BIP9 상태 중 새 규칙이 강제되기 시작하는 상태는? 정답은 C, ACTIVE입니다. DEFINED는 시작 전, STARTED는 신호를 세는 단계, LOCKED_IN은 확정만 된 단계입니다. LOCKED_IN을 고르셨다면 한 구간의 유예를 떠올려 보세요.

</details>

## Q2. Taproot 활성화에 쓰인 방식은?

- **A** 플래그 데이
- **B** BIP9 그대로
- **C** Speedy Trial
- **D** 하드포크

<details><summary>정답</summary>

**C**

Taproot 활성화에 쓰인 방식은? 정답은 C, Speedy Trial입니다. 신호를 센다는 점은 BIP9와 비슷하지만 짧은 신호 기간과 최소 활성 높이가 더해졌습니다. 플래그 데이나 하드포크가 아니었습니다.

</details>

## Q3. 시그널링에 쓰이는 블록 헤더 필드는?

- **A** nonce
- **B** bits
- **C** version
- **D** time

<details><summary>정답</summary>

**C**

시그널링에 쓰이는 블록 헤더 필드는? 정답은 C, version입니다. nonce는 채굴 탐색에, time은 블록 시각에, bits는 타깃 표시에 쓰입니다. 11-1에서 version 일부를 nonce처럼 쓰는 이야기를 했던 것도 함께 떠올려 주세요.

</details>
