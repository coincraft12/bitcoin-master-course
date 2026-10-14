# 퀴즈 · lesson-05 · 2-1 Bitcoin Core 구조: 구성 프로그램, 데이터 디렉터리, 배포본 검증, 표준 설정

슬라이드의 확인 퀴즈(CHECKPOINT)입니다. 먼저 풀어 본 뒤 정답을 펼쳐 보세요.

## Q1. 프루닝 노드가 할 수 없는 것은?

- A. 새 블록 검증
- B. 오래된 블록을 다른 노드에 제공
- C. 트랜잭션 전파
- D. 지갑 사용

<details><summary>정답과 해설</summary>

**정답 B** · 과거 블록은 지웠다

과거 블록을 지웠기 때문입니다. 새 블록 검증, 트랜잭션 전파, 지갑 사용은 프루닝 노드도 할 수 있습니다.

</details>

## Q2. 모든 트랜잭션을 txid로 조회하려면 켜야 하는 옵션은?

- A. server
- B. txindex
- C. prune
- D. fallbackfee

<details><summary>정답과 해설</summary>

**정답 B** · 프루닝과 함께 못 쓴다

server는 RPC 서버를 켜는 옵션이고, prune은 오히려 블록을 지우는 옵션이며, fallbackfee는 regtest의 수수료 기본값입니다. txindex는 프루닝과 함께 쓸 수 없다는 점도 기억하세요.

</details>

## Q3. 배포본 서명을 검증하는 이유는?

- A. 설치 속도
- B. 변조된 배포본 차단
- C. 라이선스 확인
- D. 동기화 가속

<details><summary>정답과 해설</summary>

**정답 B** · 검증하는 프로그램부터 검증

검증하는 프로그램이 변조되면 그 검증이 무의미하므로, 프로그램부터 검증합니다. 설치 속도, 라이선스, 동기화 속도와는 관계가 없습니다.

</details>

[차시 README](../part1/lesson-05/README.md)
