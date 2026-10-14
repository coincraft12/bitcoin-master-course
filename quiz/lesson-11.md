# lesson-11 퀴즈 · 3-3 레거시 주소: HASH160, Base58Check, P2SH, WIF

출처: s33-quiz 슬라이드와 나레이션.

## Q1. HASH160에 쓰이는 두 해시 함수는?

- **A** SHA256, SHA512
- **B** SHA256, RIPEMD160
- **C** MD5, SHA1
- **D** Keccak, SHA256

<details><summary>정답</summary>

**B** — RIPEMD160(SHA256(x))

HASH160에 쓰이는 두 해시 함수는 B, SHA256과 RIPEMD160입니다. SHA256으로 먼저 해시하고 그 결과를 RIPEMD160으로 해시합니다. SHA512나 MD5, Keccak은 이 과정에 쓰이지 않습니다.

</details>

## Q2. Base58 알파벳에서 빠진 문자가 아닌 것은?

- **A** 0
- **B** O
- **C** l
- **D** 1

<details><summary>정답</summary>

**D** — 1은 0x00 바이트를 표현

Base58 알파벳에서 빠진 문자가 아닌 것을 고르는 문제로 정답은 D, 숫자 1입니다. 0, 대문자 O, 소문자 l은 빠진 글자가 맞지만, 숫자 1은 알파벳에 포함되며 앞쪽 0x00 바이트를 나타내는 데 쓰입니다. 그래서 P2PKH 주소가 1로 시작합니다.

</details>

## Q3. 압축 공개키용 mainnet WIF의 첫 글자는?

- **A** 5
- **B** K 또는 L
- **C** 1
- **D** bc1

<details><summary>정답</summary>

**B** — 비압축은 5

압축 공개키용 mainnet WIF의 첫 글자는 B, K 또는 L입니다. 5는 비압축 WIF, 1은 P2PKH 주소, bc1은 SegWit 주소의 시작이므로 오답입니다.

</details>
