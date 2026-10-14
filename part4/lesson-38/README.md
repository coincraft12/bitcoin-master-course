# lesson-38 · 9-2 전파 프로토콜, 컴팩트 블록, 2노드 실습

## 목표
- 트랜잭션과 블록이 전달되는 메시지 순서를 설명한다.
- 헤더 우선 동기화와 컴팩트 블록(BIP152)의 원리를 설명한다.
- 블록 전파 속도가 채굴 중앙화와 연결되는 이유를 설명한다.

```
노드 A ── inv (txid 목록) ──▶ 노드 B     "이런 게 있어"
노드 A ◀── getdata (txid) ── 노드 B     "그거 줘" (없는 것만)
노드 A ── tx (본문) ───────▶ 노드 B     전달
```
연결 직후 version·verack로 버전과 기능 확인. 새 노드는 헤더(80바이트, 10-1)로 최다 작업 체인을 먼저 확인하고 본문은 여러 피어에서 병렬로 받는다(10-4).
컴팩트 블록: 헤더 + 트랜잭션마다 6바이트 짧은 ID → 받는 쪽이 멤풀로 재구성 → 빠진 것만 요청. 수 MB 블록이 수십 KB로. 멤풀 정책이 노드마다 너무 다르면 빠진 트랜잭션이 늘어 느려진다(8-2, 14-1).

## 파일
- `two_nodes.sh` — 실습 ① node2(/tmp/node2, P2P 18555, RPC 18556)를 띄우고 연결 (s92-lab1). `stop`으로 종료
- `watch_spread.sh` — 실습 ② 전파 관찰 (s92-lab2)

## 실습 순서
1. `two_nodes.sh`: node2를 다른 datadir·포트로 띄우고(`-debug=net`), node1에 `logging '["net"]'`, `addnode 127.0.0.1:18555 onetry` → 3초 뒤 두 노드의 `getblockcount`가 같아야 한다. `CLI2`에는 datadir과 rpcport가 함께 들어간다(빠지면 node1에 명령이 간다).
2. `watch_spread.sh`
   - 01 node1에서 alice → bob 송금 → 몇 초 뒤 node2의 `getrawmempool`에 같은 txid (바로 안 나오는 것 = 무작위 지연)
   - 02 node1에서 블록 1개 → node2 높이가 따라온다
   - 03 node2 debug.log에서 `received: inv|getdata|tx|cmpctblock|headers` 줄을 찾아 시퀀스 그림과 대조
3. 끝나면 `two_nodes.sh stop`. 이 환경은 9-3(lesson-39)과 10-3(lesson-42)에서 다시 쓴다.

## 실행
```bash
bash part4/lesson-38/two_nodes.sh          # node1(regtest, miner·alice·bob 지갑)이 떠 있어야 한다
bash part4/lesson-38/watch_spread.sh
bash part4/lesson-38/two_nodes.sh stop
```

## 기대 출력 (해시·시간은 실행마다 다름)
`two_nodes.sh`
```
Bitcoin Core starting
{ "net": true, … }
312
312
node1이 보는 피어: [{"addr":"127.0.0.1:18555","connection_type":"manual","inbound":false}]
```
두 높이(예: 312, 실행마다 다름)가 같으면 node2가 따라잡은 것이다. 다르면 몇 초 뒤 다시 확인한다. `logging` 출력은 모든 범주의 true/false 목록이다.

`watch_spread.sh`
```
# 01 node1에서 alice → bob 송금, node2 멤풀에 같은 txid가 나타나는지
TX=1e7b…c0d9                                         (실행마다 다름)
node2 멤풀에 도착: 3초 안쪽 (바로 안 나오는 이유 = 무작위 지연)   (초는 실행마다 다름)
# 02 node1에서 블록 하나 생성 → node2 높이가 따라오는지
node1 높이 313 · node2 높이 313
# 03 node2 로그에서 메시지 기록 → 시퀀스 그림(inv → getdata → tx)과 대조
2026-10-14T05:12:01Z [net] received: inv (37 bytes) peer=0
2026-10-14T05:12:01Z [net] received: tx (222 bytes) peer=0
2026-10-14T05:12:04Z [net] received: headers (82 bytes) peer=0
2026-10-14T05:12:04Z [net] received: cmpctblock (…) peer=0
…
```
node2가 받은 줄만 보이므로 `getdata`는 node2가 보낸 쪽(`sending getdata`)에서 찾는다. 로그가 비어 있으면 node2를 `-debug=net` 없이 띄웠는지 확인한다. 로그 줄의 형식(시간, 크기, peer 번호)은 버전·실행마다 다르다.

## 퀴즈
`quiz/lesson-38.md`
