# lesson-18 · 4-5 지갑 백업과 복구, 2부 미니 과제

## 목표
- 지갑 유형별로 백업해야 할 비밀 정보와 공개 정보를 구분한다.
- 니모닉 → 확장 개인키(tprv) → 디스크립터로 Core 지갑을 복구한다 (Core는 BIP39를 쓰지 않는다).
- 복구 리허설을 설계하고 실행한다: 소액으로, 다른 기기에서, 주소·잔액 대조, 정기적으로.

| 지갑 유형 | 비밀 정보 | 공개 정보·메타데이터 |
|---|---|---|
| 단일 서명 HD | 니모닉 (+패스프레이즈) | 지갑 유형·경로, 생성 시점 |
| Core 디스크립터 지갑 | 개인 디스크립터 또는 백업 파일 | 생성 시점 |
| 멀티시그 | 정족수만큼의 키 | 모든 참여자의 공개 디스크립터 |
| 타임락·상속 | 키 | miniscript 포함 정확한 디스크립터, 만료 조건 |
| 라이트닝 | 시드 | 채널 백업 (13-2) |

생성 시점은 조금 이르게 적는다. 늦게 적으면 그 전에 받은 코인을 놓친다. `listdescriptors true` 출력과 tprv는 니모닉과 같은 수준의 비밀이다 — 화면 녹화·클라우드 복사 금지.

## 파일
- `recover.py` — 4-1·4-2 코드를 재사용해 니모닉, 마스터 tprv, 첫 주소, 디스크립터 두 줄(RECV, CHG)을 출력
- `recovery_lab.sh` — 실습 ①~⑤ (s45-lab1, s45-lab2) 전체. regtest 노드와 alice·miner 지갑 필요
- `assignment/` — 2부 미니 과제 "나의 복구 키트" (README, exercise, solution)

## 실습 순서
1. `recover.py new` → 테스트 니모닉, tprv, m/84h/1h/0h/0/0 첫 주소(bcrt1q…) → alice가 0.5 BTC 송금 → 블록 1개
2. RECV(`/0/*`)·CHG(`/1/*`) 디스크립터 → `getdescriptorinfo`로 체크섬을 받아 `#xxxxxxxx` 붙이기 (빠뜨리면 가져오기 오류)
3. 빈 지갑 `recovered`(blank=true)에 `importdescriptors` (active, timestamp 0, 받는용 internal false, 잔돈용 internal true) → `getbalances`에 0.5 BTC
4. 실패 실험: `--purpose 44`(pkh + 44h), `--passphrase …`로 가져오면 잔액 0 → 4-3 체크리스트 재현
5. `backupwallet` → `restorewallet recovered_copy` → 같은 잔액

## 실행
```bash
python part2/lesson-18/recover.py new
python part2/lesson-18/recover.py show "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
python part2/lesson-18/recover.py show "<니모닉>" --purpose 44
python part2/lesson-18/recover.py show "<니모닉>" --passphrase TREZOR
bash   part2/lesson-18/recovery_lab.sh        # regtest 노드 필요
```
슬라이드의 `python3 recover.py new`는 이 폴더 안에서 실행한 모습이다. 저장소 최상위에서는 위 경로로 실행한다(어디서 실행해도 같다).

## 기대 출력
`recover.py new` (실행마다 다름)
```
니모닉   : famous hair twelve assume dish find exhaust fruit husband print arch legal (실행마다 다름)
tprv     : tprv8ZgxMBicQKsPcvbwbvdzhb3dP9WLncAFhnvFWw8GdjQfVTrwRFupQUARqEKPSu8JGfozWQ96DkLv5m3yfCYHX9TuhjxpxjkH7NzX6RDBRtg (실행마다 다름)
첫 주소  : bcrt1qgxsdjz78kv28vac7xdfzjstfqx84puwalavc6p (실행마다 다름)
RECV="wpkh(tprv8ZgxMBicQKsP…/84h/1h/0h/0/*)"
CHG="wpkh(tprv8ZgxMBicQKsP…/84h/1h/0h/1/*)"
```
`recover.py show "abandon … about"` (결정적)
```
니모닉   : abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
tprv     : tprv8ZgxMBicQKsPe5YMU9gHen4Ez3ApihUfykaqUorj9t6FDqy3nP6eoXiAo2ssvpAjoLroQxHqr3R5nE3a5dU3DHTjTgJDd7zrbniJr6nrCzd
첫 주소  : bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
RECV="wpkh(tprv8ZgxMBicQKsPe5YMU9gHen4Ez3ApihUfykaqUorj9t6FDqy3nP6eoXiAo2ssvpAjoLroQxHqr3R5nE3a5dU3DHTjTgJDd7zrbniJr6nrCzd/84h/1h/0h/0/*)"
CHG="wpkh(tprv8ZgxMBicQKsPe5YMU9gHen4Ez3ApihUfykaqUorj9t6FDqy3nP6eoXiAo2ssvpAjoLroQxHqr3R5nE3a5dU3DHTjTgJDd7zrbniJr6nrCzd/84h/1h/0h/1/*)"
```
이 두 디스크립터의 체크섬은 RECV `#tttzurp0`, CHG `#6lwrpk3h`다(Core 디스크립터 체크섬 알고리즘으로 계산). `getdescriptorinfo`가 같은 값을 돌려줘야 한다.

같은 니모닉의 실패 실험 첫 주소 (결정적)
```
--purpose 44            첫 주소  : mkpZhYtJu2r87Js3pDiWJDmPte2NRZ8bJV
--passphrase TREZOR     첫 주소  : bcrt1qfwxzlmn42rh6wu6gt4f0yrfpe4gf0jtw20y952
```
둘 다 원래 첫 주소(bcrt1q6rz28…)와 달라서, 이 디스크립터로 복구한 지갑의 잔액은 0이다.

`recovery_lab.sh` — 값은 실행마다 다름. 확인할 것: 3단계 `trusted: 0.50000000`, 1단계의 첫 주소가 `ismine: true`, `hdkeypath: m/84h/1h/0h/0/0`, 4단계 두 줄 모두 잔액 `0`, 5단계 복원 지갑도 `0.50000000`.
```
[recovered] 복구 지갑 잔액:
{ "trusted": 0.50000000, "untrusted_pending": 0.00000000, "immature": 0.00000000 }
[recovered] 첫 주소 bcrt1qgxsdjz78kv28vac7xdfzjstfqx84puwalavc6p 가 내 주소인가: (주소는 실행마다 다름)
{"ismine":true,"hdkeypath":"m/84h/1h/0h/0/0"}  (강화 표기는 Core 버전에 따라 h 또는 ')
[fail] (--purpose 44) 잔액: 0
[fail-1791974321] (--passphrase TREZOR) 잔액: 0 (지갑 이름은 실행마다 다름)
{"name":"recovered_copy"}
[recovered_copy] 잔액:
{ "trusted": 0.50000000, … }
```

## 퀴즈
`quiz/lesson-18.md`
