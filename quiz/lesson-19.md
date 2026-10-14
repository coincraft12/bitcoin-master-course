# lesson-19 퀴즈 · 5-1 입력과 출력: outpoint, 금액, 수수료, 코인베이스

출처: s51-quiz 슬라이드와 나레이션.

## Q1. outpoint를 구성하는 두 값은?

- **A** 주소, 금액
- **B** 이전 txid, 출력 인덱스
- **C** 블록 높이, txid
- **D** 공개키, 서명

<details><summary>정답</summary>

**B** — 코인 하나를 유일하게 지목

outpoint를 구성하는 두 값은 B, 이전 txid와 출력 인덱스입니다. 이 둘이 있어야 코인 하나를 유일하게 지목할 수 있습니다. 주소나 금액은 입력에 아예 없으므로 A는 틀렸고, 블록 높이나 서명은 outpoint와 관계가 없습니다.

</details>

## Q2. 입력 2 BTC, 출력 1.5 BTC와 0.4999 BTC. 수수료는?

- **A** 0
- **B** 0.0001 BTC
- **C** 0.5 BTC
- **D** 계산 불가

<details><summary>정답</summary>

**B** — 10,000 sat

수수료는 B, 0.0001 BTC입니다. 2에서 1.5와 0.4999를 빼면 0.0001 BTC, 1만 sat입니다. 수수료 칸이 없다고 계산이 불가능한 것은 아니므로 D는 아닙니다.

</details>

## Q3. 코인베이스 입력의 특징은?

- **A** scriptSig가 비어 있다
- **B** 이전 출력을 가리키지 않는다
- **C** 금액 필드가 있다
- **D** 서명이 두 개 필요하다

<details><summary>정답</summary>

**B** — txid 0, vout 0xffffffff

코인베이스 입력의 특징은 B, 이전 출력을 가리키지 않는다는 것입니다. txid가 0, vout이 0xffffffff라서 실제 출력을 가리키지 않습니다. scriptSig는 비어 있지 않고 블록 높이와 임의 데이터가 들어가므로 A는 틀렸고, 입력에는 금액 필드가 없으므로 C도 아닙니다.

</details>
