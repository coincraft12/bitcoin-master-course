# 퀴즈 · lesson-06 · 2-2 네트워크 모드: mainnet·testnet4·signet·regtest와 과정 표준 환경

슬라이드의 확인 퀴즈(CHECKPOINT)입니다. 먼저 풀어 본 뒤 정답을 펼쳐 보세요.

## Q1. 과정 실습의 기본 네트워크는?

- A. mainnet
- B. testnet4
- C. signet
- D. regtest

<details><summary>정답과 해설</summary>

**정답 D** · 진짜 돈과 분리된 실험실

regtest는 진짜 돈과 분리된 실험실이고, 블록을 즉시 만들 수 있으며 언제든 초기화할 수 있습니다. mainnet은 진짜 돈이고, testnet4와 signet은 선택 실습과 공개 데이터 실습에 씁니다.

</details>

## Q2. regtest에서 처음에 101블록을 만드는 이유는?

- A. 난이도 조정
- B. 첫 보상의 성숙에 100블록 필요
- C. 지갑 생성 조건
- D. 반감기

<details><summary>정답과 해설</summary>

**정답 B** · 코인베이스 성숙 규칙

첫 블록의 코인베이스 출력이 성숙하려면 100블록이 더 필요하기 때문입니다. 난이도 조정이나 반감기와는 관계가 없고, 지갑은 블록 없이도 만들 수 있습니다.

</details>

## Q3. bcrt1로 시작하는 주소의 네트워크는?

- A. mainnet
- B. testnet4
- C. signet
- D. regtest

<details><summary>정답과 해설</summary>

**정답 D** · tb1은 테스트, bc1은 메인

tb1은 testnet4와 signet, bc1은 mainnet입니다.

</details>

[차시 README](../part1/lesson-06/README.md)
