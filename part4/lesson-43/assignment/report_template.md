# 10강 미니 과제 보고서: 재조직 (1쪽)

## 환경
- regtest 2노드 (node1 기본 datadir, node2 /tmp/node2), Core 버전: ______
- node1: 송금 TX + 블록 2개 / node2: 송금 없는 블록 3개 (선택: 이중지불 DS 포함)

## 전후 비교
| 항목 | 재조직 전 | 재조직 후 |
|---|---|---|
| getchaintips (active / valid-fork) | | |
| 멤풀 건수 (TX가 있나) | | |
| miner 잔액 (trusted/untrusted/immature) | | |
| alice 잔액 | | |
| bob 잔액 | | |

## 원인 설명 — 10-3 "트랜잭션 운명 네 가지"
| 변화 | 해당 운명 | 이유 |
|---|---|---|
| 송금 TX가 멤풀로 돌아감 | | |
| miner의 node1 블록 보상이 사라짐 | | |
| (선택) TX가 충돌로 무효 | | |
| node2 체인의 블록들 | | |

## 결론 (3~4문장)
