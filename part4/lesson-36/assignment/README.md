# 8강 미니 과제: RBF vs CPFP 보고서 (8-5 · s8-assign)

## 과제
1. **01** 같은 조건의 저수수료 송금 두 건을 만든다 (`fee_rate` 1).
2. **02** 하나는 RBF(`bumpfee`)로, 하나는 CPFP(받는 쪽 자식)로 같은 목표 수수료율까지 가속한다.
3. **03** 총 수수료·총 vsize·확정까지 필요한 트랜잭션 수를 표로 비교하고 1쪽 보고서로 쓴다 (`report_template.md`).
   결론에 "보낸 사람이면 무엇을, 받는 사람이면 무엇을" 한 줄씩. `getmempoolentry` 출력 캡처 첨부.

핵심: 8-4 오해 장의 "CPFP는 자식 크기만큼 추가 비용이 든다"가 실제 숫자로 어떻게 나타나는지 확인한다.

## 파일
- `exercise_rbf_vs_cpfp.py` — `rbf_summary`, `cpfp_summary`, `comparison_table` 세 함수를 채운다(처음엔 NotImplementedError)
- `solution/solution_rbf_vs_cpfp.py` — 정답. `run [목표]`으로 regtest 실험 전체를 자동 실행
- `report_template.md` — 보고서 틀

## 실행 (저장소 최상위에서)
```bash
python part4/lesson-36/assignment/exercise_rbf_vs_cpfp.py
python part4/lesson-36/assignment/solution/solution_rbf_vs_cpfp.py           # 예시 수치 (노드 없이)
python part4/lesson-36/assignment/solution/solution_rbf_vs_cpfp.py run 10    # regtest 노드, miner·alice·bob 지갑
```
CPFP 자식은 입력 1·출력 1(110 vB로 가정)로 만들고, 패키지 수수료율이 목표가 되도록 자식 수수료율 = ⌈(목표 × (부모 vsize + 110) − 부모 수수료) ÷ 110⌉로 정한다.

## 정답 기대 출력
예시 수치 (결정적 · 실측이 아니라 계산 확인용: 부모 141 vB·141 sat, 목표 10 sat/vB)
```
예시 수치(실측 아님, 계산 확인용):
방식        총 수수료(sat)   총 vsize(vB)    실효(sat/vB)      트랜잭션 수
RBF             1410           141         10.00           1
CPFP            2510           251         10.00           2
CPFP 추가 비용: 1100 sat (자식 크기만큼)
```
같은 목표 수수료율이면 CPFP는 자식 110 vB × 10 sat/vB = 1,100 sat를 더 낸다.

`run 10` (txid·값은 실행마다 다름)
```
원본 두 건: 61f0…d2e3 9a8c…44b1                       (실행마다 다름)
getmempoolentry (보고서에 첨부):
RBF 대체본 {"vsize": 141, "fees": {"base": "0.00001410", …}}
CPFP 부모 {"vsize": 141, "fees": {"base": "0.00000141", "ancestor": …, "descendant": "0.00002561", …}}
CPFP 자식 {"vsize": 110, "fees": {"base": "0.00002420", …}}
방식        총 수수료(sat)   총 vsize(vB)    실효(sat/vB)      트랜잭션 수
RBF             1410           141         10.00           1
CPFP            2561           251         10.20           2
CPFP 추가 비용: 1151 sat (자식 크기만큼)
블록 1개로 확정. 자식 수수료율 22 sat/vB, 대체본 수수료 0.00001410 BTC
```
자식 수수료율을 정수로 올림(⌈21.54⌉ = 22)해서 실효가 목표보다 조금 높다. alice 지갑이 고른 입력에 따라 부모 vsize가 달라지면 표의 숫자도 달라진다. 자식 수수료는 지갑의 서명 크기 추정 때문에 몇 sat 다를 수 있다.

## 결론 예
- 보낸 사람이면: RBF. 원본을 대체하므로 추가 트랜잭션 크기가 없다.
- 받는 사람이면: CPFP. 원래 입력의 키가 없어 RBF를 쓸 수 없다. 자식 크기만큼 더 낸다.
