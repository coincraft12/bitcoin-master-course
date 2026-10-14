# lesson-42 · 10-3 체인 선택과 재조직

## 목표
- 최다 누적 작업량 규칙을 설명한다.
- 재조직을 재현하고 트랜잭션에 생기는 일을 설명한다.
- 확인 수와 이중지불 확률, 51% 공격의 한계를 설명한다.

"가장 긴"이 아니라 "가장 무거운" 체인: 블록 수만 세면 난이도 낮은 블록을 대량으로 만든 긴 체인으로 속일 수 있다 → 각 블록 타깃(10-1)에서 계산한 작업량을 합산한다.

| 재조직에서 트랜잭션의 운명 (s103-reorg) | 결과 |
|---|---|
| 새 체인에도 있는 것 | 그대로 확정 |
| 새 체인에 없지만 유효한 것 | 멤풀로 돌아와 다음 블록을 기다린다 |
| 새 체인 트랜잭션과 같은 입력을 쓰던 것 | 무효가 되어 사라진다 → 이중지불이 노리는 지점 |
| 버려진 블록의 코인베이스 보상 | 사라진다 → 그래서 100블록 성숙 규칙(2-2) |

## 파일
- `double_spend_prob.py` — 백서 11절 계산식으로 확인 수 표 재계산, 긴 체인 vs 무거운 체인 (노드 없이)
- `reorg_lab.sh` — 실습 ①~④ (s103-lab1, s103-lab2). 9-2의 2노드 환경 필요

## 실습 순서
1. `$CLI2 setnetworkactive false`로 두 노드 분리 — 먼저 실행하지 않으면 블록이 바로 전파되어 버린다.
2. node1: alice → bob 0.3 BTC(TX) + 블록 2개 → TX 2 확인.
3. node2: 지갑 m2를 만들고 송금 없는 블록 3개 → 더 무거운 체인.
4. 재연결(`setnetworkactive true`, `addnode … onetry`, 5초) → `getchaintips`에 node1의 2블록 가지가 `valid-fork`로 남고, node1은 node2의 3블록 체인으로 갈아탄다. TX는 멤풀로 복귀(confirmations null 또는 0), miner 지갑의 2블록 보상은 `orphan`.
5. 질문: node2에서 같은 alice 코인을 다른 곳으로 보내는 트랜잭션을 먼저 넣었다면 TX는? → 이중지불의 정확한 구조(10강 미니 과제 선택 항목, lesson-43).

## 실행
```bash
python part4/lesson-42/double_spend_prob.py
bash   part4/lesson-38/two_nodes.sh      # 2노드 환경
bash   part4/lesson-42/reorg_lab.sh
```

## 기대 출력
`double_spend_prob.py` (결정적)
```
공격자 해시 비율 | 성공 확률 0.1% 미만이 되는 확인 수
           10% |   5
           15% |   8
           20% |  11
           25% |  15
           30% |  24
q = 10%, z = 0..6: 1.0000000 0.2045873 0.0509779 0.0131722 0.0034552 0.0009137 0.0002428
== 가장 긴 체인이 아니라 가장 무거운 체인 (block_work = 2^256 ÷ (타깃 + 1)) ==
regtest 난이도 블록 10개 작업량 20 · 난이도 1 블록 1개 작업량 4295032833 → 무거운 쪽: 짧은 체인
```
슬라이드 s103-confirm 표(5, 8, 11, 15, 24)와 같다. 관행 6 확인은 하나의 기준점일 뿐, 필요한 확인 수는 금액과 상대 해시파워 가정으로 정한다.

`reorg_lab.sh` (해시·높이는 실행마다 다름)
```
# 시작: node1 높이 313, node2 높이 313 (같아야 한다)
…
2
[ "…", "…", "…" ]
[
  { "height": 316, "hash": "6e2a…", "branchlen": 0, "status": "active" },
  { "height": 315, "hash": "1f9c…", "branchlen": 2, "status": "valid-fork" }
]
0
null
# getbestblockhash: 재연결 전 1f9c… → 후 6e2a… (node2 tip 6e2a…)
# miner 잔액(재조직 후): {"trusted":…,"untrusted_pending":0,"immature":…}
# miner 지갑에서 사라진 블록 보상 (category orphan):
{"category":"orphan","amount":…,"blockhash":"…"}
{"category":"orphan","amount":…,"blockhash":"…"}
# 다음 블록에서 TX 다시 확정
TX 확인 수: 1
```
`getrawmempool | jq 'index($t)'`는 TX의 멤풀 위치(0 이상)를 낸다. null이면 아직 재조직이 일어나지 않은 것이니 몇 초 뒤 다시 본다. confirmations는 Core 버전에 따라 null 또는 0이다.

## 퀴즈
`quiz/lesson-42.md`
