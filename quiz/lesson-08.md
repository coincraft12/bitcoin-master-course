# 퀴즈 · lesson-08 · 2-4 Python으로 노드 제어: RPC 래퍼, Decimal, 1부 미니 과제

슬라이드의 확인 퀴즈(CHECKPOINT)입니다. 먼저 풀어 본 뒤 정답을 펼쳐 보세요.

## Q1. 특정 지갑에 RPC를 보내는 URL 경로는?

- A. `/rpc/<지갑명>`
- B. `/wallet/<지갑명>`
- C. `/<지갑명>/rpc`
- D. 경로 없이 헤더로

<details><summary>정답과 해설</summary>

**정답 B** · /wallet/alice

alice라면 /wallet/alice입니다. 다른 보기의 경로는 Bitcoin Core가 쓰지 않는 형식이고, 헤더로 지갑을 지정하지도 않습니다.

</details>

## Q2. RPC 응답에서 오류를 담는 필드는?

- A. result
- B. id
- C. error
- D. status

<details><summary>정답과 해설</summary>

**정답 C** · 본문부터 읽는다

result는 결과, id는 요청과 응답을 짝짓는 값이고, status라는 필드는 없습니다. HTTP 상태가 실패여도 본문에 error가 있으므로 본문부터 읽습니다.

</details>

## Q3. 금액을 Decimal로 파싱하는 이유는?

- A. 속도
- B. 부동소수점 반올림 오차 방지
- C. 메모리 절약
- D. 노드 요구사항

<details><summary>정답과 해설</summary>

**정답 B** · 계산은 sat 정수로

속도나 메모리 때문이 아니고, 노드가 요구하는 것도 아닙니다. 그리고 내부 계산은 sat 정수로 합니다.

</details>

[차시 README](../part1/lesson-08/README.md)
