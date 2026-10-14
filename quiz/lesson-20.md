# lesson-20 퀴즈 · 5-2 직렬화와 witness: CompactSize, 가변성, txid·wtxid, weight·vsize, 파서

출처: s52-quiz 슬라이드와 나레이션.

## Q1. txid와 wtxid의 차이는?

- **A** 해시 함수가 다르다
- **B** witness 포함 여부
- **C** 바이트 순서
- **D** 차이 없다

<details><summary>정답</summary>

**B** — txid는 witness 제외

txid와 wtxid의 차이는 B, witness 포함 여부입니다. txid는 witness를 제외하고, wtxid는 포함해서 계산합니다. 둘 다 같은 이중 SHA256을 쓰므로 A는 아니고, 바이트 순서 표시 관례도 둘이 같으므로 C도 아닙니다.

</details>

## Q2. 기본 200바이트, 전체 300바이트. vsize는?

- **A** 200
- **B** 225
- **C** 250
- **D** 300

<details><summary>정답</summary>

**B** — 900 WU ÷ 4

vsize는 B, 225입니다. weight가 200 곱하기 3 더하기 300으로 900 WU이고, 4로 나누면 225 vB입니다. 기본 크기 200이나 전체 크기 300을 그대로 고르면 할인 공식을 빼먹은 것입니다.

</details>

## Q3. SegWit이 해결한 대표 문제는?

- **A** 이중지불
- **B** 제3자에 의한 트랜잭션 가변성
- **C** 51% 공격
- **D** 주소 재사용

<details><summary>정답</summary>

**B** — 서명이 txid에서 빠졌다

SegWit이 해결한 대표 문제는 B, 제3자에 의한 트랜잭션 가변성입니다. 서명이 txid 계산에서 빠졌기 때문입니다. 이중지불이나 51퍼센트 공격은 SegWit과 무관한 문제입니다.

</details>
