# 4부 미니 과제: 내 노드로 만든 네트워크 리포트 (11-5 · s11-assign)

regtest(메인넷 노드가 있으면 메인넷)에서 다음을 자동으로 계산하는 스크립트를 작성하고 1쪽 보고서로 정리한다.
1. **01** 최근 블록 N개의 평균 크기·weight, 블록당 트랜잭션 수, 평균 수수료율 (8-1)
2. **02** 블록 간 시간 간격 분포와 평균 (11-1 무기억성 확인)
3. **03** 코인베이스 태그 상위 집계 또는 regtest 보조금 변화 (11-2·11-3)
4. **04** 10강 재조직 실습 결과 요약 (10-3)

제출물: 스크립트, 실행 결과, 보고서(`report_template.md`) · 메인넷 데이터를 쓰면 가산점.

## 파일
- `exercise_network_report.py` — `block_summary`, `interval_stats`, `subsidy_changes`를 채운다(처음엔 NotImplementedError)
- `solution/solution_network_report.py` — 정답. 인자 없이 예시 수치, `regtest N` 또는 `main N`으로 실제 노드
- `report_template.md` — 보고서 틀

## 실행 (저장소 최상위에서)
```bash
python part4/lesson-48/assignment/exercise_network_report.py
python part4/lesson-48/assignment/solution/solution_network_report.py               # 예시 수치 (노드 없이)
python part4/lesson-48/assignment/solution/solution_network_report.py regtest 300
python part4/lesson-48/assignment/solution/solution_network_report.py main 1000     # 메인넷 노드 (수 분 걸린다)
```
값은 `getblockstats`(total_size, total_weight, txs, avgfeerate, subsidy, time)에서 온다. 평균 수수료율은 블록별 avgfeerate를 코인베이스를 뺀 트랜잭션 수로 가중 평균한다. 메인넷의 03은 11-3 `coinbase_tags.py`와 같은 방식이다.

## 정답 기대 출력
인자 없이 (결정적 · 예시 수치, 실측 아님)
```
예시 수치(실측 아님, 형식 확인용):
== 01 블록 ==
  blocks: 5
  avg_size: 666.0
  avg_weight: 2194.4
  avg_txs: 2.4
  avg_feerate: 7.86
== 02 블록 간격 (초) ==
  평균 600.0 · 최소 60 · 최대 1080
       0~299    # 1
     300~599    # 1
     600~899    # 1
     900~1199   # 1
== 03 보조금 변화 (regtest 반감 주기 150) ==
  구간 148~152 첫 보조금 5000000000 sat
  높이 150: 2500000000 sat (subsidy(h, 150)과 일치)
== 04 재조직 요약: 10강 보고서를 붙인다 ==
```
`regtest 300`: 4부 실습을 차례로 했다면 높이가 수백이므로 03에 반감 높이(150의 배수)마다 한 줄씩 나온다. regtest 블록은 몇 초 안에 몰아서 만들어져 02의 간격이 거의 0초에 몰린다 — 무기억성은 메인넷 데이터로 확인해야 하는 이유를 보고서에 적는다.
