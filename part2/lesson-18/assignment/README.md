# 2부 미니 과제: 나의 복구 키트 (4-5 · s45-assign)

> 실제 자금의 니모닉은 절대 제출하지 않는다. 공개된 테스트 니모닉이나 regtest에서 새로 만든 니모닉만 쓴다.

## 제출물
1. **01** 테스트 니모닉으로 BIP84·BIP86 첫 주소를 3개씩 계산 — `exercise_recovery_kit.py`의 함수 세 개를 채운다.
2. **02** 그 니모닉을 Core에 디스크립터로 복원해 계산한 주소와 Core가 만든 주소가 일치하는지 캡처.
3. **03** 가상의 2-of-3 멀티시그 복구 키트 문서 1쪽 — `recovery_kit_template.md`를 채운다(무엇을, 어디에, 누가). 모든 공개 디스크립터를 각 보관 장소에 함께 두었는지 스스로 점검한다.

## 실행 (저장소 최상위에서)
```bash
python part2/lesson-18/assignment/exercise_recovery_kit.py "<테스트 니모닉>"   # 처음엔 NotImplementedError
python part2/lesson-18/assignment/solution/solution_recovery_kit.py            # 정답 (기본: abandon ×11 + about)
bash   part2/lesson-18/assignment/solution/restore_in_core.sh                  # 02 예시 (regtest 노드 필요)
```

## 정답 기대 출력 (테스트 니모닉 abandon ×11 + about, 직접 실행해 확인한 값)
```
자체 확인 (공식 벡터 BIP84 2개, BIP86 2개): True
BIP84 (regtest, m/84h/1h/0h/0/0..2):
  bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
  bcrt1qd7spv5q28348xl4myc8zmh983w5jx32cs707jh
  bcrt1qxdyjf6h5d6qxap4n2dap97q4j5ps6ua8jkxz0z
BIP86 (regtest, m/86h/1h/0h/0/0..2):
  bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg
  bcrt1p90h6z3p36n9hrzy7580h5l429uwchyg8uc9sz4jwzhdtuhqdl5eqkcyx0f
  bcrt1p40qqa84kpphe5vtcwd8zv7v6w7p62cmupf6f60mf8pxdkcv2455qgtw98j
RECV84="wpkh(tprv8ZgxMBicQKsPe5YMU9gHen4Ez3ApihUfykaqUorj9t6FDqy3nP6eoXiAo2ssvpAjoLroQxHqr3R5nE3a5dU3DHTjTgJDd7zrbniJr6nrCzd/84h/1h/0h/0/*)"
CHG84=… /84h/1h/0h/1/*)   RECV86="tr(… /86h/1h/0h/0/*)"   CHG86=… /86h/1h/0h/1/*)
```
- 자체 확인은 mainnet 경로(m/84h/0h/0h/0/i, m/86h/0h/0h/0/i)를 BIP84·BIP86 문서의 공식 벡터와 대조한 결과다.
- regtest는 coin_type `1h`, HRP `bcrt`. Core regtest 지갑과 같은 규칙이다(4-3).
- BIP86 주소는 6-4의 출력키 조정(`lib/taproot.py`의 `output_key`)을 미리 쓴다.

## 02 캡처 예 (`restore_in_core.sh` · 지갑 이름은 실행마다 다름, 주소는 두 열이 같아야 한다)
```
[true,true,true,true]
== 대조 (지갑 kit-1791974000) ==
BIP84 #0 계산 bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk  Core bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
…
BIP86 #2 계산 bcrt1p40qqa84kpphe5vtcwd8zv7v6w7p62cmupf6f60mf8pxdkcv2455qgtw98j  Core bcrt1p40qq…
```
두 열이 모두 같아야 한다. 다르면 4-3 잔액 0 진단 체크리스트(경로·purpose·패스프레이즈)로 원인을 찾는다.

## 03 참고
`solution/recovery_kit_example.md` — 작성 예시. 핵심: 비밀(니모닉)은 흩어 두고, 공개 디스크립터는 모든 키 보관 장소에 함께 둔다(s45-multisig).
