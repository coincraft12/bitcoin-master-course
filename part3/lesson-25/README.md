# lesson-25 · 6-3 타임락: nLockTime, nSequence, CLTV, CSV 실습

## 목표
- 절대·상대 × 트랜잭션·스크립트 수준의 네 조합(nLockTime · nSequence(BIP68) · CLTV(BIP65) · CSV(BIP112))을 구분한다.
- 각각의 동작 조건(높이/시간 경계 5억, MTP, 31·22번 비트, OP_DROP이 필요한 이유)을 설명한다.
- miniscript(`after`, `older`)로 타임락 출력을 만들고 기한 전후 지출 결과를 확인한다.

## 코드
- `timelock_lab.sh` — LAB ①~④ (s63-lab1~3): 20블록 뒤에야 쓸 수 있는 코인, 기한 전 지출 두 가지, 기한 후 지출
- `csv_assignment.sh` — s63-lab3 과제 · CSV 버전 `older(10)` 정답 예
- `timelock_fields.py` — 노드 없이: nLockTime·nSequence 값 해석, CLTV·CSV 잠금 스크립트 바이트

## 실습 순서
1. **키와 만료 높이** participant_1(6-2)의 `listdescriptors true`에서 tprv를 꺼낸다 — **regtest 전용 키만**(영상에는 "regtest 전용" 자막). H = 현재 높이 + 20, `wsh(and_v(v:pk(TPRV/7/*),after(H)))` + 체크섬.
2. **지갑 tl** 빈 지갑에 range [0,5]로 가져오고 `deriveaddresses`로 첫 주소에 1 BTC 입금.
3. **기한 전 두 가지**
   - (a) locktime = 현재 높이 < H → `walletprocesspsbt`의 `complete: false` (miniscript 만족 계산이 after를 채울 수 없음 = **스크립트 조건** 문제)
   - (b) locktime = H → 서명·finalize까지 되지만 `sendrawtransaction`이 **non-final**로 거부 (**트랜잭션 유효 시점** 문제). 이 HEX를 지우지 않는다.
4. **기한 후** 블록 20개 → (b)의 HEX를 그대로 다시 보내면 성공. 미리 서명해 두고 때가 되면 전파하는 패턴(상속·채널).
5. **과제 · CSV** `wsh(and_v(v:pk(TPRV/8/*),older(10)))`, 입력에 `sequence 10` 명시 → 확정 직후와 10블록 뒤 비교.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-25/timelock_fields.py      # 노드 없이
bash   part3/lesson-25/timelock_lab.sh         # regtest, participant_1(lesson-24)·miner·bob 지갑
bash   part3/lesson-25/csv_assignment.sh       # 과제 정답 예
```

## 기대 출력
`timelock_fields.py` (결정적, 직접 실행한 값)
```
nLockTime
   0 → 즉시 유효
   800000 → 블록 높이 800000 이후 블록부터 포함 가능
   1700000000 → 유닉스 시간 1700000000 이후 (직전 11블록 중앙값 시간 MTP 기준, BIP113)
nSequence (BIP68)
   0xffffffff → 최종: nLockTime 무시, RBF 신호 없음, 상대 타임락 없음
   0xfffffffd → RBF 신호(8-3), 31번 비트 1 → 상대 타임락 비활성
   0x00000090 → RBF 신호(8-3), 상대 타임락 144 (블록 수) = 확정 후 약 하루
   0x004000a9 → RBF 신호(8-3), 상대 타임락 169 (512초 단위 시간) = 86,528초 ≈ 24시간
   0x80000000 → RBF 신호(8-3), 31번 비트 1 → 상대 타임락 비활성

<820000> OP_CHECKLOCKTIMEVERIFY OP_DROP <공개키> OP_CHECKSIG
   0320830cb175210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ac
<144> OP_CHECKSEQUENCEVERIFY OP_DROP <공개키> OP_CHECKSIG
   029000b275210279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798ac
상대 타임락 상한 65,535 블록(약 455일) · 1년 ≈ 52,560블록은 older(52560)으로 표현 가능: 0350cd00
```

`timelock_lab.sh` (높이·주소·txid는 실행마다 다름)
```
만료 높이 H=233 (실행마다 다름)
[true]
TL_ADDR=bcrt1qr7pxh7hn684tm65nmxy5pd8z277305km0a7qs2mkcsg7hqh3lnpsfrk7sx (실행마다 다름)
== (a) nLockTime=214 < 만료 높이: 스크립트 조건 미충족 ==
false
== (b) nLockTime=233 = 만료 높이: 서명은 되지만 아직 그 높이가 아님 ==
error code: -26
error message:
non-final
→ 기대한 거부: non-final (트랜잭션 유효 시점 문제)
e2bb6396a96d625555316dabb10b0fbaea0a485077f62c9f6b8842ada63aafa8 (실행마다 다름)
→ 같은 바이트가 이번엔 받아들여졌다. 새로 만든 트랜잭션이 아니다.
```
- (a)에서 Core 버전에 따라 PSBT 생성 단계부터 거절될 수도 있다. 어느 쪽이든 "스크립트 조건을 채울 수 없음"이 요점이다.
- 슬라이드 명령 그대로면 tl 지갑이 잔돈 주소를 만들지 못해 `walletcreatefundedpsbt`가 실패한다. 저장소 스크립트는 같은 디스크립터의 1번 주소를 `changeAddress`로 지정한다(ERRATA s63-lab2).

`csv_assignment.sh` (실행마다 다름)
```
[true]
== 확정 직후 (1 confirmation) ==
{"allowed":false,"reject-reason":"non-BIP68-final"}
== 10 confirmations 뒤 (다음 블록이 11번째) ==
{"allowed":true,"reject-reason":null}
7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95 (실행마다 다름)
```

## 퀴즈
`quiz/lesson-25.md`
