# 12강 미니 과제: 우리 집 상속·복구 설계 1쪽 (12-4 · s12-assign)

> **실제 키 정보(니모닉·xprv·패스프레이즈·실주소)는 절대 기재 금지.** 과제 자체가 이번 강의의 원칙("위치와 절차는 쓰고, 비밀은 쓰지 않는다")을 지키는 연습이다.

본인 가족 상황을 가정해 다음 네 가지를 한 쪽에 정리한다.

| 번호 | 내용 | 관련 |
|---|---|---|
| 01 | 위협 모델 요약 — 우리 집에서는 무엇을, 누가, 어떻게 노릴 수 있나 (자산·공격자·경로·대응) | 12-1 |
| 02 | 복구 경로 정책 — miniscript 한 줄과 N을 그렇게 정한 이유 | 12-4 |
| 03 | 리프레시 주기와 담당, 상속 문서 목차 (넣을 것 / 넣지 말 것) | 12-4 |
| 04 | 리허설 계획 — 누가, 언제, 무엇을 연습하나 | 12-4, 4-5 |

## 파일
- `exercise_estate_plan.md` — 채워 쓸 1쪽 양식
- `solution/estate_plan_example.md` — 작성 예시 (가상의 가족)
- `solution/check_no_secrets.py` — 제출 전 점검: 니모닉·확장 개인키·WIF·실주소가 문서에 남아 있는지 찾는다

## 제출 전 점검 (저장소 최상위에서)
```bash
python part5/lesson-52/assignment/solution/check_no_secrets.py 내_설계.md
```
예시 문서를 점검하면 (직접 실행해 확인한 출력)
```
$ python part5/lesson-52/assignment/solution/check_no_secrets.py part5/lesson-52/assignment/solution/estate_plan_example.md
금지 0건, 주의 0건
→ 실제 키 정보가 보이지 않는다. 그래도 한 번 더 직접 읽어 본다.
```
공개된 테스트 니모닉·tprv·주소를 일부러 넣은 문서를 점검하면
```
[금지] 니모닉으로 보이는 단어열: abandon abandon abandon … (12단어)
[금지] 확장 개인키 tprv8ZgxMBic…
[금지] 주소 mkpZhYtJu2r87Js3pDiWJDmPte2NRZ8bJV
[금지] 주소 bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
[주의] 패스프레이즈 값으로 보이는 줄: 패스프레이즈: TREZOR1
금지 4건, 주의 1건
→ 제출하지 않는다. 비밀은 지우고 '위치'만 남긴다.
```
종료 코드는 금지 항목이 있으면 1, 없으면 0. 점검 스크립트는 보조 수단이다 — 사진·스캔 이미지 속 비밀이나 한국어로 풀어 쓴 단어는 찾지 못한다.

## 평가 포인트
- 02의 miniscript가 "평시 본인 단독, N블록 미사용 후 가족" 구조인가: `or(pk(본인),and(pk(가족),older(N)))` 또는 그 확장(s124-patterns).
- N ≤ 65,535블록(약 15개월). 1년 ≈ 52,560블록. 리프레시 주기가 N보다 충분히 짧은가.
- 상속 문서 목차에 디스크립터(공개)·복구 안내서·연락처·백업 위치가 있고, 니모닉·패스프레이즈 원문이 없는가.
- 리허설이 실제로 지출까지 해 보는 계획인가 (lesson-52 `estate_lab.sh`처럼 regtest 또는 소액).
