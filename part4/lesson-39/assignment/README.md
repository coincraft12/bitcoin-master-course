# 9강 미니 과제: 내 노드 네트워크 보고서 (9-3 · s9-assign)

## 과제
1. **01** 내 노드(또는 2노드 환경)의 `getpeerinfo` 분석: 방향·연결 유형·전송 방식 분포 (9-1 실습 코드 활용)
2. **02** 2노드 환경에서 트랜잭션 1건·블록 1개의 전파 로그를 시퀀스 그림으로 다시 그리기 (9-2)
3. **03** 내가 쓰는 지갑이 SPV·블록 필터·서버 질의 중 무엇인지 확인하고 노출되는 정보 1문단 (9-3)

IP 등 개인 정보는 가리고 제출한다. 보고서 틀은 `report_template.md`.

## 파일
- `exercise_network_report.py` — `peer_distribution`, `parse_net_log`, `sequence_diagram`을 채운다(처음엔 NotImplementedError)
- `solution/solution_network_report.py` — 정답. 인자 없이 실행하면 가상 예시 로그로 형식을 보여 준다
- `report_template.md` — 보고서 틀

## 실행 (저장소 최상위에서)
```bash
python part4/lesson-39/assignment/exercise_network_report.py
python part4/lesson-39/assignment/solution/solution_network_report.py
bash   part4/lesson-38/two_nodes.sh && bash part4/lesson-38/watch_spread.sh     # 로그 만들기
python part4/lesson-39/assignment/solution/solution_network_report.py regtest /tmp/node2/regtest/debug.log
```

## 정답 기대 출력
인자 없이 (결정적 · 가상 예시 로그, 실제 로그 아님)
```
가상 예시 로그(형식 확인용):
2026-10-14T05:12:01Z  node1 ── inv ──▶ node2
2026-10-14T05:12:01Z  node2 ── getdata ──▶ node1
2026-10-14T05:12:01Z  node1 ── tx ──▶ node2
2026-10-14T05:12:04Z  node1 ── headers ──▶ node2
2026-10-14T05:12:04Z  node1 ── cmpctblock ──▶ node2
```
`ping` 같은 전파와 무관한 메시지는 걸러진다.

`regtest /tmp/node2/regtest/debug.log` (값은 실행마다 다름)
```
== 01 피어 분포 ==
방향: {'outbound': 1}
연결 유형: {'manual': 1}
전송 방식: {'v2': 1}
== 02 전파 시퀀스 (마지막 40개) ==
2026-10-14T05:12:01Z  node1 ── inv ──▶ node2
…
```
피어 분포는 node1 기준(node2에 `addnode … onetry`로 연결한 1개)이다.

## 03 작성 힌트 (9-3 s93-methods)
- 블룸 필터(BIP37): 주소가 상당 부분 드러남, Core 기본 비활성
- 블록 필터(BIP157/158): 노드는 "이 지갑이 블록 X를 요청했다"만 안다
- 서버 질의(Electrum 등): 서버가 모든 주소를 안다 → 내 풀노드에 Electrum 서버를 붙이는 것이 실무 해법
