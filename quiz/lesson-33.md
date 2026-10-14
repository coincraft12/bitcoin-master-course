# lesson-33 퀴즈 · 8-2 멤풀 정책: 합의 vs 정책, 정책 항목, 더스트 실습

출처: s82-quiz 슬라이드와 나레이션.

## Q1. 릴레이 정책을 바꾸는 데 포크가 필요한가?

- **A** 소프트포크 필요
- **B** 하드포크 필요
- **C** 필요 없음
- **D** 채굴자 투표 필요

<details><summary>정답</summary>

**C**

릴레이 정책을 바꾸는 데 포크가 필요할까요? 정답은 C, 필요 없습니다. 정책은 노드 설정이나 버전 변경만으로 바뀝니다. 소프트포크나 하드포크는 합의 규칙을 바꿀 때 필요하고, 채굴자 투표라는 절차도 정책 변경과는 관계가 없습니다.

</details>

## Q2. 멤풀이 가득 차면 어떤 것부터 축출되나?

- **A** 가장 오래된 것
- **B** 수수료율이 가장 낮은 것
- **C** 금액이 가장 작은 것
- **D** 무작위

<details><summary>정답</summary>

**B**

멤풀이 가득 차면 어떤 것부터 축출될까요? 정답은 B, 수수료율이 가장 낮은 것부터입니다. 오래된 순서나 금액, 무작위가 아니라 채굴자에게 가장 가치가 낮은 것부터 내보냅니다.

</details>

## Q3. 전파 없이 정책 통과 여부만 확인하는 RPC는?

- **A** sendrawtransaction
- **B** decoderawtransaction
- **C** testmempoolaccept
- **D** getmempoolinfo

<details><summary>정답</summary>

**C**

전파 없이 정책 통과 여부만 확인하는 RPC는 무엇일까요? 정답은 C, testmempoolaccept입니다. sendrawtransaction은 실제로 전파하고, decoderawtransaction은 해석만 하며, getmempoolinfo는 멤풀 상태를 보여줍니다.

</details>
