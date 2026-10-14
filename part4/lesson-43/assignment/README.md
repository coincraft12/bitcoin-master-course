# 10강 미니 과제: 재조직 보고서 (10-4 · s10-assign)

## 과제
1. **01** regtest 2노드로 재조직을 만든다 (10-3 실습).
2. **02** 재조직 전후의 `getchaintips`·멤풀·지갑 잔액 변화를 표로.
3. **03** 1쪽 보고서: 각 변화의 원인을 10-3의 "트랜잭션 운명 네 가지"로 설명 (`report_template.md`).
4. 선택: 같은 alice 코인을 node2에서 다른 곳으로 보내 이중지불까지 재현.

## 파일
- `exercise_reorg_report.py` — `tx_fate`, `snapshot_table`을 채운다(처음엔 NotImplementedError)
- `solution/solution_reorg_report.py` — 정답. `run`은 2노드 환경에서 재조직 전체를 자동 실행, `--double-spend`는 선택 항목까지
- `report_template.md` — 보고서 틀

## 실행 (저장소 최상위에서)
```bash
python part4/lesson-43/assignment/exercise_reorg_report.py
python part4/lesson-43/assignment/solution/solution_reorg_report.py                     # 예시 수치 (노드 없이)
bash   part4/lesson-38/two_nodes.sh
python part4/lesson-43/assignment/solution/solution_reorg_report.py run
python part4/lesson-43/assignment/solution/solution_reorg_report.py run --double-spend
```
node2의 RPC 포트는 18556이라 `lib/rpc.py`의 `RPC(datadir="/tmp/node2")`를 만든 뒤 `url`만 바꿔 쓴다(rpc.py는 고치지 않는다).

## 정답 기대 출력
인자 없이 (결정적 · 예시 수치, 실측 아님)
```
예시 수치(실측 아님, 형식 확인용):
항목                                                                   재조직 전                             재조직 후
최고 높이                                                                  313                               316
활성 tip                                                               1f9c…                             6e2a…
valid-fork 가지 수                                                          0                                 1
멤풀 건수                                                                    0                                 1
miner trusted/untrusted/immature (sat)          24000000000/0/500000000000        24000000000/0/500000000000
bob trusted/untrusted/immature (sat)                         500000000/0/0              500000000/30000000/0
송금 TX: 멤풀로 복귀
버려진 블록 보상: 코인베이스 보상 소멸
이중지불된 TX: 충돌로 무효
```

`run --double-spend` (값은 실행마다 다름)
```
DS(같은 입력을 alice에게) node2에 제출: 0a7d…e4c2            (실행마다 다름)
항목 …                                                    재조직 전   재조직 후
…
getchaintips (후):
  active       height 316 branchlen 0 6e2a…
  valid-fork   height 315 branchlen 2 1f9c…
송금 TX 4f3b…: confirmations -3 → 충돌로 무효   (DS가 node2의 블록 3개 중 첫 블록에 담겨 3 확인)
node1이 캔 블록 5c10… → 코인베이스 보상 소멸
node1이 캔 블록 1f9c… → 코인베이스 보상 소멸
miner 지갑 orphan 항목: 2
```
`--double-spend` 없이 `run`하면 송금 TX는 `confirmations 0 → 멤풀로 복귀`다. 충돌한 지갑 트랜잭션의 confirmations는 음수(충돌한 트랜잭션이 받은 확인 수)로 표시된다.
