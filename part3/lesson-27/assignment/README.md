# 6강 미니 과제: 상속형 Taproot 지갑 설계 (6-5 · s6-assign)

## 과제
1. **01** 구조: 평소엔 2-of-2 MuSig2 **키 경로**, 비상시엔 "1년(약 52,560블록) 뒤 **복구 키 단독**" **리프**.
2. **02** `tr()` 디스크립터를 작성하고 `getdescriptorinfo`로 체크섬까지 검증한다.
3. **03** 설계 근거 1쪽: 왜 키 경로/리프에 두었나, 타임락 상한(65,535) 확인, 복구 키트에 무엇을 남기나.

MuSig2 키는 7-4에서 직접 만든다. 이번엔 **자리표시 키**로 구조만 잡는다. 결과는 12-4 상속 설계의 출발점.

## 파일
- `exercise_inheritance.py` — 채울 함수 세 개(`leaf_script`, `descriptor`, `address`). 처음엔 NotImplementedError.
- `solution/solution_inheritance.py` — 정답: 리프 스크립트 바이트, 디스크립터(체크섬 포함), regtest 주소를 노드 없이 계산
- `solution/check_with_core.sh` — 02: Core `getdescriptorinfo`·`deriveaddresses`로 체크섬·주소 대조
- `solution/design_rationale.md` — 03 작성 예
- `solution/descriptors.py` — Bitcoin Core `test/functional/test_framework/descriptors.py` 원본(MIT, BIP380 체크섬). 노드 없이 체크섬을 계산하려고 둔다.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-27/assignment/exercise_inheritance.py              # 처음엔 NotImplementedError
python part3/lesson-27/assignment/solution/solution_inheritance.py     # 정답 (노드 없이)
bash   part3/lesson-27/assignment/solution/check_with_core.sh         # regtest 노드로 체크섬·주소 대조
```

## 정답 기대 출력 (결정적, 직접 실행한 값)
자리표시 키: 집계키 자리 = 테스트 니모닉 m/86h/1h/0h/0/0, 복구 키 = m/86h/1h/1h/0/0의 x-only 공개키.
```
타임락 52560블록 ≤ 상한 65535: True (약 365일)
리프 스크립트 39 B: 20340404d6ca0d8a9b019d3ac3527ad2ac063c60446fdd13e76c0d2e5704c10163ad0350cd00b2
리프 해시 = 머클 루트 (잎 하나): True 540ae90fb9a6db7236153f1804e1f1ec98bd06c8a1a20ba994c742519967a68d
디스크립터: tr(55355ca83c973f1d97ce0e3843c85d78905af16b4dc531bc488e57212d230116,and_v(v:pk(340404d6ca0d8a9b019d3ac3527ad2ac063c60446fdd13e76c0d2e5704c10163),older(52560)))#kkgkujt6
체크섬 검사: True
주소 (regtest): bcrt1p6jj9jgf0swc9l6ke7amc7fvw6s5skamafd945utq6hq00feschkqzkg5za
복구 지출 witness: [복구키 서명 64B, 리프 스크립트 39B, 컨트롤 블록 33B] · 입력 nSequence 52560 · 트랜잭션 version 2
평소 지출 witness: [집계키 서명 64B] — 단일 서명 지갑과 구분할 수 없다
```
- 리프 스크립트 = `<복구키> OP_CHECKSIGVERIFY <52560> OP_CHECKSEQUENCEVERIFY`. 52,560 = 0xcd50 → 스크립트 숫자는 리틀 엔디안 `50 cd`, 최상위 비트가 1이라 부호용 `00`을 덧붙여 `03 50cd00`.
- 잎이 하나라 머클 경로가 없고 컨트롤 블록은 1 + 32 = 33바이트.
- 체크섬 `#kkgkujt6`은 Core의 BIP380 체크섬 코드로 계산했다(같은 코드가 BIP380의 `raw(deadbeef)#89f8spxm` 예를 재현).

`check_with_core.sh` (regtest 노드 · 아래는 Core가 같은 규칙으로 내야 하는 값)
```
DESC=tr(55355ca83c973f1d97ce0e3843c85d78905af16b4dc531bc488e57212d230116,and_v(v:pk(340404d6ca0d8a9b019d3ac3527ad2ac063c60446fdd13e76c0d2e5704c10163),older(52560)))#kkgkujt6
{"checksum":"kkgkujt6","isrange":false,"issolvable":true,"hasprivatekeys":false}
Core 주소 : bcrt1p6jj9jgf0swc9l6ke7amc7fvw6s5skamafd945utq6hq00feschkqzkg5za
내 계산   : bcrt1p6jj9jgf0swc9l6ke7amc7fvw6s5skamafd945utq6hq00feschkqzkg5za
```
이 작업 환경에는 노드가 없어 Core 출력은 직접 확인하지 못했다. 두 주소가 다르면 miniscript 컴파일(리프 바이트)부터 의심한다.

## 제출물
디스크립터(체크섬 포함), `getdescriptorinfo` 결과, 설계 근거 1쪽.
