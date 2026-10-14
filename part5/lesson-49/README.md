# lesson-49 · 12-1 위협 모델과 사례, 주소 중독 실습

## 목표
- 자산·공격자·경로·대응이라는 네 질문으로 위협 모델을 세운다 (s121-model).
- 개인과 기관의 주요 위협을 분류하고 기본 방어책을 연결한다 (s121-threats1·2, s121-checklist).
- 주소 중독 같은 인터페이스 공격의 원리를 직접 시연한다 (s121-lab).

공격자는 수학을 깨지 않는다. 사람과 소프트웨어, 키 관리의 빈틈을 노린다.

| 위협 | 기본 방어 | 차시 |
|---|---|---|
| 키 유출 | 오프라인 서명기, 니모닉 오프라인 보관 | 4-5, 12-2 |
| 피싱·가짜 앱 | 공식 경로 설치, "니모닉을 묻는 곳은 모두 사기" | — |
| 클립보드 하이재킹 | 서명기 화면에서 주소 전체 확인 | 5-4 |
| 주소 중독 | 거래 내역에서 주소 복사 금지, 주소록·전체 대조 | **이번 실습** |
| 서명 유도 | 서명 전 디코딩·검증 | 7-4, 5-4 |
| 논스·구현 결함 | 검증된 구현, anti-exfil | 7-2 |
| 공급망 | 서명 검증, 공식 판매처 | 2-1, 12-2 |
| 물리적 강요 | 노출 최소화, 멀티시그·타임락으로 즉시 인출 불가 구조 | 12-3, 12-4 |
| 내부자 | 멀티시그·정족수·승인 정책 | 12-3 |

기본 방어 원칙 7가지(s121-checklist): ① 니모닉은 서명 기기 외 디지털 기기에 입력·저장하지 않는다 ② 주소는 출처 확인·전체 대조 ③ 서명은 서명 기기 화면에서 확인한 내용에만 ④ 큰 금액은 단일 키에 두지 않는다 ⑤ 소프트웨어·장비는 공식 경로, 서명 검증 ⑥ 보유 사실을 드러내지 않는다 ⑦ 복구 절차를 정기적으로 리허설한다.

## 파일
- `address_poisoning.py` — s121-lab 슬라이드 코드 그대로 (저장소 루트를 sys.path에 넣는 줄만 추가). 노드 필요 없음
- `detect_poison.py` — 막는 쪽 보조 도구: 지갑 화면처럼 줄여 보기 vs 전체 대조, 주소록과 앞뒤 끝 글자가 닮은 주소 경고. 노드 필요 없음

## 실습 순서
1. `address_poisoning.py` 실행 → 피해자 주소와 앞 8자(`bcrt1q` + 2글자)·끝 1자가 같은 가짜 주소를 찾을 때까지 기다린다. 맞출 글자 3개 → 기대 32³ = 32,768번. 순수 파이썬 초당 약 100~120개 → 평균 4~5분.
2. 두 주소를 앞 8자·뒤 4자만 남겨 띄워 보고 구별되는지 본다 → `detect_poison.py demo`(슬라이드의 두 주소)로 같은 비교를 바로 볼 수 있다.
3. `detect_poison.py check`로 주소록 대조: 주소록에 있는 주소는 "안전", 닮았지만 다른 주소는 "경고", 처음 보는 주소는 "미확인".
4. 글자 하나 늘 때마다 32배 → GPU 공격자는 훨씬 많은 글자를 맞춘다. 앞뒤 몇 글자 확인으로는 부족하다.

교육 목적. 실제 주소를 대상으로 가짜 주소를 만들지 말 것.

## 실행 (저장소 최상위에서)
```bash
python part5/lesson-49/address_poisoning.py          # 수 분 걸린다
python part5/lesson-49/detect_poison.py demo
python part5/lesson-49/detect_poison.py search       # 2글자짜리 가짜 주소를 새로 찾아 비교 (수 초~수십 초)
python part5/lesson-49/detect_poison.py check 주소록.txt 후보주소 [후보주소 ...]
```

## 기대 출력
`address_poisoning.py` (실행마다 다름 · 이 저장소에서 직접 실행했을 때 16,416번, 2분 49초)
```
bcrt1qvesqlts5llke2806ykw5autzzzh0dc63tep26m
bcrt1qvejpmy49yntgqngv3prr5hhzjh035q4c3xmxum
시도: 16416
```
슬라이드 실행 예는 10,596번, 88초다. 시도 횟수는 기하분포라 들쭉날쭉하다(평균 32,768).

`detect_poison.py demo` (결정적 — 슬라이드 s121-lab의 두 주소)
```
[줄여 보기] 지갑 화면처럼 앞 8자·뒤 4자만
    bcrt1qzw…ury4   ← 주소록
    bcrt1qzw…jc34   ← 거래 내역
[전체 대조] ^ = 다른 글자
    bcrt1qzws2nuwwpwwkq69hpgt9ncuyj4k6y46fjlury4   ← 주소록
    bcrt1qzwmgzg8wvh06c9f2tyhjrhhnyy54tsttgzjc34   ← 거래 내역
            ^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
[탐지] 고정부(bcrt1q) 뒤 앞 2자·끝 1자 일치 → 중독 의심
```
`check` (주소록 파일에 슬라이드의 피해자 주소 한 줄, 후보 세 개)
```
$ python part5/lesson-49/detect_poison.py check book.txt bcrt1qzwmgzg8wvh06c9f2tyhjrhhnyy54tsttgzjc34 bcrt1qzws2nuwwpwwkq69hpgt9ncuyj4k6y46fjlury4 bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
경고  bcrt1qzwmgzg8wvh06c9f2tyhjrhhnyy54tsttgzjc34  (주소록 주소와 앞 2자·뒤 1자가 같지만 다른 주소)
      bcrt1qzws2nuwwpwwkq69hpgt9ncuyj4k6y46fjlury4  ← 주소록
              ^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
안전  bcrt1qzws2nuwwpwwkq69hpgt9ncuyj4k6y46fjlury4  (주소록에 있음)
미확인 bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk  (주소록에 없음 — 출처를 따로 확인)
```
경고가 있으면 종료 코드 1. 기본 기준은 고정부 뒤 앞뒤 끝 일치 글자 합 3개 이상(무작위 두 주소가 우연히 이럴 확률은 수천 분의 1).

## 흔히 막히는 지점
- `ModuleNotFoundError: lib` — 저장소 최상위가 아닌 곳에서 `python address_poisoning.py`로 실행해도 맨 위 두 줄이 루트를 찾아 주지만, 파일을 다른 폴더로 복사하면 깨진다. 저장소 안에서 실행한다.
- 오래 걸린다 — 정상이다. 기다리기 어려우면 `detect_poison.py search`(2글자)로 원리를 먼저 본다.
- "앞 8자"에는 모든 P2WPKH regtest 주소에 공통인 `bcrt1q` 6자가 들어 있다. 실제로 맞춘 글자는 3개다.

## 퀴즈
`quiz/lesson-49.md`
