# lesson-16 퀴즈 · 4-3 파생 경로 표준: purpose, 갭 리밋, 잔액 0 진단

출처: s43-quiz 슬라이드와 나레이션.

## Q1. bc1q 주소용 표준 경로의 purpose는?

- **A** 44'
- **B** 49'
- **C** 84'
- **D** 86'

<details><summary>정답</summary>

**C** — BIP84

bc1q 주소용 표준 경로의 purpose는 C, 84입니다. BIP84입니다. 44는 1로 시작하는 P2PKH, 49는 3으로 시작하는 중첩 SegWit, 86은 bc1p로 시작하는 Taproot입니다.

</details>

## Q2. 경로의 change 자리가 1이면?

- **A** 두 번째 계정
- **B** 잔돈 주소 체인
- **C** testnet
- **D** 강화 파생

<details><summary>정답</summary>

**B** — 0 받는 주소, 1 잔돈

경로의 change 자리가 1이면 B, 잔돈 주소 체인입니다. 0이면 받는 주소, 1이면 잔돈입니다. 두 번째 계정은 account 자리가 바꾸고, testnet은 coin_type 자리가 나타내며, 강화 파생 여부는 h 표시로 나타냅니다.

</details>

## Q3. 잔액 0의 흔한 원인이 아닌 것은?

- **A** 패스프레이즈 누락
- **B** purpose 불일치
- **C** 갭 리밋
- **D** 블록 난이도 변화

<details><summary>정답</summary>

**D** — 난이도는 지갑과 무관

잔액 0의 흔한 원인이 아닌 것은 D, 블록 난이도 변화입니다. 난이도는 채굴과 관련된 값으로 지갑 복구와는 관계가 없습니다. 패스프레이즈 누락, purpose 불일치, 갭 리밋은 모두 체크리스트에 있는 흔한 원인입니다.

</details>
