# 퀴즈 · lesson-07 · 2-3 bitcoin-cli와 RPC: JSON-RPC 구조, 조회 연쇄, RPC 보안

슬라이드의 확인 퀴즈(CHECKPOINT)입니다. 먼저 풀어 본 뒤 정답을 펼쳐 보세요.

## Q1. 블록 높이로 블록 해시를 얻는 RPC는?

- A. getblock
- B. getblockhash
- C. getblockchaininfo
- D. getrawtransaction

<details><summary>정답과 해설</summary>

**정답 B** · 높이 → 해시

높이를 넣으면 해시가 나옵니다. getblock은 해시를 넣어 블록을 받는 명령이고, getblockchaininfo는 체인 전체 상태를, getrawtransaction은 트랜잭션을 조회합니다.

</details>

## Q2. verbosity 3에서 2보다 추가로 보이는 것은?

- A. 블록 hex
- B. 입력이 쓴 이전 출력 정보
- C. 멤풀 정보
- D. 지갑 잔액

<details><summary>정답과 해설</summary>

**정답 B** · 수수료 계산의 재료

각 입력이 쓴 이전 출력의 금액과 스크립트가 붙고, 이것이 수수료 계산의 재료가 됩니다. 블록 hex는 verbosity 0의 결과이고, 멤풀 정보나 지갑 잔액은 getblock이 주는 정보가 아닙니다.

</details>

## Q3. bitcoin-cli가 노드와 통신하는 방식은?

- A. P2P 프로토콜
- B. HTTP 위의 JSON-RPC
- C. 파일 공유
- D. WebSocket

<details><summary>정답과 해설</summary>

**정답 B** · 그래서 curl로도 된다

그래서 curl로도, 어떤 언어로도 같은 일을 할 수 있습니다. P2P 프로토콜은 노드끼리 블록과 트랜잭션을 주고받는 방식이고, 파일 공유나 WebSocket은 해당하지 않습니다.

</details>

[차시 README](../part1/lesson-07/README.md)
