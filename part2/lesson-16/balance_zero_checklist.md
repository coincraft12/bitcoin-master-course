# 잔액 0 진단 체크리스트 (4-3 · 수강생 배포용 1쪽)

"니모닉을 다른 앱에 넣었더니 잔액이 0입니다." — 대부분 코인은 그대로 있고, 지갑이 다른 가지를 보고 있을 뿐이다. 위에서부터 차례로 확인한다.

| # | 확인 | 어떻게 |
|---|---|---|
| 1 | 니모닉 철자와 단어 순서 | 체크섬이 우연히 맞아도(16분의 1) 순서가 틀리면 다른 지갑이다. 앞 4글자로 단어를 대조한다. |
| 2 | 패스프레이즈 사용 여부 | 패스프레이즈가 빠지거나 대소문자·띄어쓰기 하나만 달라도 오류 없이 빈 지갑이 열린다. |
| 3 | 주소 유형·purpose | 예전 주소가 1… → 44′, 3… → 49′, bc1q… → 84′, bc1p… → 86′. |
| 4 | 계정 번호 | 0′이 아닌 계정(1′, 2′ …)을 썼을 수 있다. |
| 5 | 갭 리밋 | 주소를 대량으로 미리 발급한 이력(결제 서버 등)이 있으면 갭 리밋(기본 20)을 늘린다. |
| 6 | 비표준 경로 | 표준 정착 전 일부 구형 지갑의 독자 경로인지 확인한다. |

가장 흔한 원인은 **3번과 4번**이다.

## 경로 한 줄 읽기
`m / purpose′ / coin_type′ / account′ / change / index`
- coin_type: 0′ = 비트코인 mainnet, 1′ = testnet·signet·regtest (Core regtest 디스크립터의 `1h`)
- change: 0 = 받는 주소, 1 = 잔돈 주소
- 계정까지 강화(′), 그 아래는 일반 파생

## 예: 공개된 테스트 니모닉(abandon ×11 + about)
| 경로 | 주소 |
|---|---|
| m/44h/0h/0h/0/0 | 1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA |
| m/49h/0h/0h/0/0 | 37VucYSaXLCAsxYyAPfbSi9eh4iEcbShgf |
| m/84h/0h/0h/0/0 | bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu |
| m/84h/0h/0h/1/0 (잔돈) | bc1q8c6fshw2dlwun7ekn9qwf37cu2rn755upcp6el |
| m/84h/0h/1h/0/0 (두 번째 계정) | bc1qku0qh0mc00y8tk0n65x2tqw4trlspak0fnjmfz |
| m/86h/0h/0h/0/0 | bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr |

같은 니모닉에서 나온 여섯 주소가 모두 다르다. 테스트 니모닉이므로 실제 자금에 절대 쓰지 않는다.
