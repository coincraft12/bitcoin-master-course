# lesson-13 퀴즈 · 3-5 Taproot 주소: bech32m, P2TR, 유형별 크기 비교

출처: s35-quiz 슬라이드와 나레이션.

## Q1. bech32m이 도입된 이유는?

- **A** 주소 길이 단축
- **B** 마지막 글자 앞 삽입·삭제를 놓치는 약점
- **C** 양자 내성
- **D** 대문자 지원

<details><summary>정답</summary>

**B** — 상수 하나로 해결

bech32m이 도입된 이유는 B, 마지막 글자 앞 문자의 삽입과 삭제를 놓치는 bech32의 약점 때문입니다. 체크섬 상수 하나만 바꿔 해결했습니다. 주소 길이 단축이나 양자 내성, 대문자 지원과는 관계가 없습니다.

</details>

## Q2. P2TR 출력에 들어가는 것은?

- **A** 공개키의 HASH160
- **B** 32바이트 x-only 출력키
- **C** 스크립트의 SHA256
- **D** 압축 공개키 33바이트

<details><summary>정답</summary>

**B** — 해시가 아닌 키

P2TR 출력에 들어가는 것은 B, 32바이트 x-only 출력키입니다. 해시가 아니라 키가 그대로 들어간다는 것이 핵심입니다. 공개키의 HASH160은 P2WPKH, 스크립트의 SHA256은 P2WSH의 내용이고, 33바이트 압축 공개키는 P2TR에서 쓰지 않습니다.

</details>

## Q3. 단일 서명 기준 입력 크기가 가장 작은 유형은?

- **A** P2PKH
- **B** P2SH-P2WPKH
- **C** P2WPKH
- **D** P2TR

<details><summary>정답</summary>

**D** — 약 57.5 vB

단일 서명 기준 입력 크기가 가장 작은 유형은 D, P2TR입니다. 키 경로 입력이 약 57.5 vB로, P2WPKH의 약 68 vB, P2SH-P2WPKH의 약 91 vB, P2PKH의 약 148 vB보다 작습니다.

</details>
