# lesson-48 · 11-5 소프트포크 활성화, 4부 미니 과제

## 목표
- 버전 비트 시그널링(BIP9)의 상태 전이를 단계별로 설명한다.
- SegWit과 Taproot 활성화를 비교하고 Speedy Trial의 배경을 설명한다.
- 노드에서 배포 상태를 조회하고 regtest에서 활성화를 재현한다.

```
DEFINED ─(시작 시각)─▶ STARTED ─(신호 ≥ 임계치)─▶ LOCKED_IN ─(한 구간 뒤)─▶ ACTIVE
STARTED ─(만료 시각까지 미달)─▶ FAILED
```
채굴자가 헤더 version(10-1)의 특정 비트를 켜고, 노드가 2016블록 구간마다 센다. 임계치: SegWit 95%, Taproot 90%(2016 중 1,815). 시그널링은 투표가 아니라 준비 상태 조율이지만, BIP9에서는 사실상 채굴자 거부권이라는 비판(2017 교착).
Taproot(메인넷, Core 소스): bit 2, nStartTime 2021-04-24, nTimeout 2021-08-11, min_activation_height 709,632, 1,815/2,016.

## 코드
`lib/block.py`가 보탠 것: `signals_bit(version, bit)` — version이 BIP9 형식(상위 3비트 001)이고 그 비트가 켜졌는지. 상수 `VERSIONBITS_TOP_BITS = 0x20000000`.

## 파일
- `deployments.sh` — 실습 ① 배포 상태 (s115-lab1)
- `testdummy_lab.sh` — 실습 ② regtest에서 testdummy 활성화 재현 (s115-lab2) + 헤더 version 확인
- `header_versions.py` — 높이별 헤더 version을 10-1 파서로 (regtest 노드)
- `bip9_sim.py` — 같은 상태 전이를 노드 없이 계산 (Core 31 regtest 파라미터)
- `assignment/` — 4부 미니 과제 "내 노드로 만든 네트워크 리포트" (README, exercise, solution)

## 실습 순서
1. `deployments.sh`: bip34·bip65·bip66·csv·segwit은 `buried`(활성 높이가 코드에 고정), taproot는 Core 31까지 `bip9`로 표시, testdummy는 시험용. Core 32 출시 준비판 릴리스 노트 초안: taproot 항목 제거 → "항상 활성"으로 가정하거나 Core 31부터 있는 `script_flags`의 TAPROOT로 확인. 자기 노드 버전을 먼저 본다.
2. `env/reset_regtest.sh`로 새 regtest에서 시작(이전 실습으로 체인이 길면 이미 활성일 수 있다 — 많이 막히는 곳) → `testdummy_lab.sh`: 144블록씩 세 번 만들며 testdummy 상태를 본다.
   - 144: started (시작 시각 0 → 두 번째 구간부터 신호 집계, Core 템플릿이 bit 28을 자동으로 켠다)
   - 288: locked_in (앞 구간 144블록 모두 신호 ≥ 108)
   - 432: active (한 구간 뒤, 이후 블록은 bit 28을 끈다)
3. 블록 version: 신호 구간 0x30000000(상위 001 + bit 28) → 활성 후 0x20000000.
4. 선택: 메인넷 노드가 있다면 2021년 Taproot 신호 기간 블록에서 bit 2 비율을 구간별로 집계해 차트로.

## 실행
```bash
python part4/lesson-48/bip9_sim.py
bash   part4/lesson-48/deployments.sh
bash   env/reset_regtest.sh && bash part4/lesson-48/testdummy_lab.sh
```

## 기대 출력
`bip9_sim.py` (결정적)
```
tip  status     since
144  started    144
288  locked_in  288
432  active     432
높이별 헤더 version:
  143: 0x20000000  bit28=False
  144: 0x30000000  bit28=True
  287: 0x30000000  bit28=True
  288: 0x30000000  bit28=True
  431: 0x30000000  bit28=True
  432: 0x20000000  bit28=False
신호가 임계치에 못 미치면 (구간당 107블록만 신호):
  432: started  (만료 시각이 없어 started에 머문다)
```
`python part4/lesson-48/bip9_sim.py 102`(setup_regtest.sh 뒤 높이 102에서 시작)이면 tip이 246·390·534로 바뀔 뿐 status와 since(144·288·432)는 같다.

`deployments.sh` (Core 31.1 regtest)
```
Bitcoin Core RPC client version v31.1.0
{ "name": "bip34", "type": "buried", "active": true, "height": 1 }
{ "name": "bip66", "type": "buried", "active": true, "height": 1 }
{ "name": "bip65", "type": "buried", "active": true, "height": 1 }
{ "name": "csv", "type": "buried", "active": true, "height": 1 }
{ "name": "segwit", "type": "buried", "active": true, "height": 0 }
{ "name": "testdummy", "type": "bip9", "active": false, "height": null }
{ "name": "taproot", "type": "bip9", "active": true, "height": 0 }
# script_flags (Core 31~)
["P2SH", …, "TAPROOT"]   (배열에 TAPROOT가 있으면 Taproot 규칙 적용 중)
```
buried 높이는 Core 소스 regtest 값(BIP34·65·66·CSV 1, SegWit 0)이다. 체인이 짧으면 active가 false로 나올 수 있고, 항목 순서·testdummy 상태·script_flags 목록과 위치는 버전과 높이에 따라 다르다(필드가 없으면 안내 문구가 나온다).

`testdummy_lab.sh` (새 regtest, 높이 0에서 시작)
```
시작 높이 0
{"status":"started","since":144}
{"status":"locked_in","since":288}
{"status":"active","since":432}
# 블록 version을 10-1 파서로: 신호 구간 0x30000000 → 활성 후 0x20000000
 143: 0x20000000  bit28=False
 144: 0x30000000  bit28=True
 287: 0x30000000  bit28=True
 288: 0x30000000  bit28=True
 431: 0x30000000  bit28=True
 432: 0x20000000  bit28=False
# 같은 결과를 노드 없이 계산: python3 part4/lesson-48/bip9_sim.py 0
```
노드 값은 슬라이드(Core 31 소스 기준 파라미터)와 `bip9_sim.py`의 계산이 같아야 한다.

## 퀴즈
`quiz/lesson-48.md`
