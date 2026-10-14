# lesson-12 퀴즈 · 3-4 SegWit 주소: bech32, P2WPKH, P2WSH, 중첩 SegWit

출처: s34-quiz 슬라이드와 나레이션.

## Q1. P2WPKH와 P2WSH의 witness 프로그램 길이는?

- **A** 20, 20
- **B** 20, 32
- **C** 32, 32
- **D** 33, 32

<details><summary>정답</summary>

**B** — HASH160 vs SHA256

P2WPKH와 P2WSH의 witness 프로그램 길이는 B, 20바이트와 32바이트입니다. P2WPKH는 공개키의 HASH160이라 20바이트, P2WSH는 스크립트의 SHA256이라 32바이트입니다. 33바이트는 압축 공개키 길이이니 D는 오답입니다.

</details>

## Q2. bech32 주소에서 마지막 '1'의 역할은?

- **A** 버전
- **B** HRP와 데이터의 구분자
- **C** 체크섬 시작
- **D** 네트워크 표시

<details><summary>정답</summary>

**B** — 구분자

bech32 주소에서 마지막 1의 역할은 B, HRP와 데이터를 나누는 구분자입니다. 버전은 그 바로 뒤 글자가 나타내고, 네트워크는 HRP가 나타내며, 체크섬은 끝 6글자입니다.

</details>

## Q3. regtest SegWit v0 주소의 접두어는?

- **A** bc1q
- **B** tb1q
- **C** bcrt1q
- **D** 2

<details><summary>정답</summary>

**C** — HRP bcrt

regtest SegWit v0 주소의 접두어는 C, bcrt1q입니다. regtest의 HRP가 bcrt이기 때문입니다. bc1q는 mainnet, tb1q는 testnet과 signet이고, 2는 regtest의 P2SH 주소가 시작하는 글자입니다.

</details>
