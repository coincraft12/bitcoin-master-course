# lesson-31 퀴즈 · 7-4 Sighash와 MuSig2, 3부 미니 과제

출처: s74-quiz 슬라이드와 나레이션.

## Q1. 다른 사람이 입력을 추가할 수 있게 하는 플래그는?

- **A** NONE
- **B** SINGLE
- **C** ANYONECANPAY
- **D** DEFAULT

<details><summary>정답</summary>

**C**

다른 사람이 입력을 추가할 수 있게 하는 플래그는 무엇일까요? 정답은 C, ANYONECANPAY입니다. 자기 입력 하나만 고정하기 때문입니다. NONE과 SINGLE은 출력 쪽 범위를 정하는 플래그이고, DEFAULT는 ALL과 같은 범위입니다.

</details>

## Q2. BIP341이 모든 입력 금액을 서명 해시에 넣은 이유는?

- **A** 속도 향상
- **B** 수수료 검증·다중 입력 금액 속이기 방지
- **C** 블록 크기 절감
- **D** 하위 호환

<details><summary>정답</summary>

**B**

BIP341이 모든 입력 금액을 서명 해시에 넣은 이유는 무엇일까요? 정답은 B입니다. 서명기가 수수료를 확실히 검증하도록, 그리고 다중 입력에서 금액을 속이는 공격을 막기 위해서입니다. 속도나 블록 크기, 하위 호환과는 관계가 없습니다.

</details>

## Q3. MuSig2가 기본적으로 지원하는 구조는?

- **A** 1-of-n
- **B** m-of-n
- **C** n-of-n
- **D** 제한 없음

<details><summary>정답</summary>

**C**

MuSig2가 기본적으로 지원하는 구조는 무엇일까요? 정답은 C, n-of-n입니다. m-of-n은 FROST나 스크립트 경로 조합이 필요합니다.

</details>
