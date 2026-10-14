# lesson-16 · 4-3 파생 경로 표준: purpose, 갭 리밋, 잔액 0 진단

## 목표
- `m/purpose′/coin_type′/account′/change/index` 다섯 자리를 해석한다.
- purpose(44·49·84·86)와 주소 유형(P2PKH·P2SH-P2WPKH·P2WPKH·P2TR)을 대응시켜 유형별 주소를 만든다.
- 지갑을 옮겼을 때 잔액이 0으로 보이는 문제를 진단한다 → `balance_zero_checklist.md` (배포용 1쪽).

## 실습 순서 (s43-code)
1. 테스트 니모닉 abandon ×11 + about을 패스프레이즈 없이 시드로
2. `pub(path)`로 각 표준의 첫 받는 주소: 44h → `p2pkh_address`, 49h → `p2sh_p2wpkh_address`, 84h → `p2wpkh_address`
3. 기대값과 대조. BIP86(bc1p…)은 출력키 조정이 필요해 6-4에서 직접 계산하지만, 이 저장소에는 6-4 코드(`lib/taproot.py`)가 미리 들어 있어 같이 출력한다.
4. 과제: m/84h/0h/0h/1/0 잔돈 주소와 m/84h/0h/1h/0/0 두 번째 계정 주소가 모두 다름을 확인하고 체크리스트 3·4번과 연결해 설명

## 실행
```bash
python part2/lesson-16/four_addresses.py
```

## 기대 출력 (결정적)
```
1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA
37VucYSaXLCAsxYyAPfbSi9eh4iEcbShgf
bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu
bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr

[과제] BIP84
첫 받는 주소    m/84h/0h/0h/0/0  bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu
첫 잔돈 주소    m/84h/0h/0h/1/0  bc1q8c6fshw2dlwun7ekn9qwf37cu2rn755upcp6el
두 번째 계정    m/84h/0h/1h/0/0  bc1qku0qh0mc00y8tk0n65x2tqw4trlspak0fnjmfz
regtest 첫 주소 m/84h/1h/0h/0/0  bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
```
- 84h 첫 받는 주소·첫 잔돈 주소, 86h 첫 받는 주소는 BIP84·BIP86 문서의 테스트 벡터와 같다(`tests/test_bip32.py`가 확인).
- 44h·49h mainnet 값은 BIP 문서에 벡터가 없어 직접 계산한 값이다. BIP49 문서의 벡터는 testnet(m/49′/1′/0′/0/0 → 2Mww8dCYPUpKHofjgcXcBCEGmniw9CoaiD2)이며 테스트에서 함께 확인한다 (ERRATA 참고).
- regtest 줄은 4-4·4-5 실습에서 Core가 만드는 주소와 같은 규칙(coin_type 1h, HRP bcrt)이다.

> 공개된 테스트 니모닉 · 실제 자금에 절대 쓰지 말 것.

## 퀴즈
`quiz/lesson-16.md`
