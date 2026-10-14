# lesson-24 퀴즈 · 6-2 멀티시그: CHECKMULTISIG, P2SH·P2WSH, 2-of-3 PSBT 실습

출처: s62-quiz 슬라이드와 나레이션.

## Q1. 해제 스크립트 맨 앞에 빈 값이 들어가는 이유는?

- **A** 서명 개수 표시
- **B** CHECKMULTISIG가 값을 하나 더 꺼내는 버그
- **C** 수수료 계산용
- **D** 버전 표시

<details><summary>정답</summary>

**B** — NULLDUMMY

해제 스크립트 맨 앞에 빈 값이 들어가는 이유는 B, CHECKMULTISIG가 값을 하나 더 꺼내는 버그 때문입니다. 지금은 NULLDUMMY 규칙으로 반드시 빈 값이어야 합니다. 서명 개수나 버전을 표시하는 값이 아닙니다.

</details>

## Q2. Tapscript에서 멀티시그 조건에 쓰는 opcode는?

- **A** OP_CHECKMULTISIG
- **B** OP_CHECKSIGADD
- **C** OP_CHECKSEQUENCEVERIFY
- **D** OP_RETURN

<details><summary>정답</summary>

**B** — CHECKMULTISIG는 비활성

Tapscript에서 멀티시그 조건에 쓰는 opcode는 B, OP_CHECKSIGADD입니다. Tapscript에서는 CHECKMULTISIG가 비활성화되고 CHECKSIGADD로 서명 수를 셉니다. CHECKSEQUENCEVERIFY는 타임락, OP_RETURN은 데이터 기록용입니다.

</details>

## Q3. 멀티시그와 MPC의 온체인 차이는?

- **A** 차이 없음
- **B** 멀티시그는 조건이 보이고 MPC는 단일 서명
- **C** MPC가 더 비싸다
- **D** 멀티시그는 Taproot 불가

<details><summary>정답</summary>

**B**

멀티시그와 MPC의 온체인 차이는 B, 멀티시그는 조건이 드러나고 MPC는 단일 서명으로 보인다는 것입니다. 멀티시그도 Taproot로 만들 수 있으므로 D는 틀렸습니다.

</details>
