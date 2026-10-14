# lesson-36 · 8-5 TRUC와 클러스터 멤풀, 8강 미니 과제

## 목표
- 피닝 공격의 원리와 L2에 위험한 이유를 설명한다.
- TRUC(v3) 트랜잭션 규칙과 피닝 완화 방식을 설명한다.
- 클러스터 멤풀이 개선하는 한계를 설명한다.

| TRUC 규칙 (BIP431, version = 3) | 효과 |
|---|---|
| 미확정 부모 최대 1개, 미확정 자식 최대 1개 | 가족 크기 2로 고정 |
| TRUC 부모의 자식은 1,000 vB 이하 | 거대한 자식 피닝 차단 |
| TRUC 트랜잭션 자체 10,000 vB 이하 | 대체 비용 예측 가능 |
| TRUC의 자식도 TRUC | 규칙 일관성 |
| 새 자식이 기존 자식을 대체 가능 (형제 축출) | 상대가 붙인 자식에 막히지 않음 |

Core 28부터 version 3이 모든 네트워크에서 표준(합의가 아니라 옵트인 릴레이 정책). 임시 앵커: 수수료 0 부모 + P2A 앵커 + 앵커를 쓰는 자식 — Core 28.0(TRUC, 1P1C, P2A), 29.0(임시 더스트).
클러스터 멤풀(Core 31.0, 2026년 4월): 클러스터 한도 64개·101 kvB, 교체 후 피레이트 다이어그램이 엄격히 더 좋아야 수락, CPFP carve-out 제거, 새 RPC `getmempoolcluster`·`getmempoolfeeratediagram`.

## 파일
- `truc_lab.sh` — 실습 ① v3 부모, ②③ 자식 두 개 시도와 v2 비교 (s85-lab1, s85-lab2)
- `assignment/` — 8강 미니 과제 "RBF vs CPFP 보고서" (README, exercise, solution)

## 실습 순서
1. bob에게 0.1 BTC → `fundrawtransaction`(fee_rate 2) → hex 앞 8글자(version)를 `03000000`으로 바꾼 뒤 서명 → `decoderawtransaction`으로 version 3 확인 → 전파. 질문: 왜 서명 전에 바꿔야 하나? → version도 서명 해시에 포함(7-4).
2. A: 부모의 bob 출력을 쓰는 v3 자식(bob 지갑) → 수락.
3. B: 부모의 잔돈 출력을 쓰는 v3 자식(alice 지갑) → 5 sat/vB면 거부, 50 sat/vB면 첫 자식을 형제 축출하고 수락. 결과와 거부 메시지를 활동지에 기록한다.
4. C: 같은 실험을 v2로 → 자식 두 개 모두 수락.

스크립트는 자식도 부모와 같은 방식(`createrawtransaction` → 앞 4바이트 교체 → `signrawtransactionwithwallet`)으로 만든다. TRUC 부모의 자식은 TRUC여야 하는데, 지갑 `send`에 version 지정 옵션이 없는 버전이 있어서다. 자식은 입력 1·출력 1(110 vB로 보고 수수료 = 수수료율 × 110 sat), A는 10 sat/vB.

## 실행
```bash
bash part4/lesson-36/truc_lab.sh        # regtest 노드(Core 28 이상), miner·alice·bob 지갑, jq 필요
```

## 기대 출력 (txid는 실행마다 다름)
```
######## ① version 3 부모 ########
3
PARENT=2c41…7f0a                                    (실행마다 다름)
######## ②-A 첫 번째 v3 자식: 부모의 bob 출력 (bob 지갑, 10 sat/vB) ########
수락 A=e9d0…13b6                                    (실행마다 다름)
######## ②-B 두 번째 v3 자식: 부모의 잔돈 출력 (alice 지갑) ########
-- 5 sat/vB (첫 자식보다 절대 수수료가 작다)
error code: -26
error message:
insufficient fee (including sibling eviction), …
-- 50 sat/vB (첫 자식보다 절대 수수료가 크다 → 형제 축출)
수락 B=71ab…c45e                                    (실행마다 다름)
A가 멤풀에 있나: false
B가 멤풀에 있나: true
부모의 자손: ["71ab…c45e"]
…
######## ③ 같은 실험을 v2로 ########
version: 2
수락 A2=…
수락 B2=…
v2 부모의 자손 수: 2
블록 1개로 정리 완료
```
슬라이드 실측(Core 31.1): 둘째 자식 5 sat/vB → "insufficient fee (including sibling eviction)" 거부, 50 sat/vB → 첫 자식을 축출하고 수락, v2는 둘 다 수락. 형제 축출 조건은 RBF 규칙과 같다 — 기존 형제보다 절대 수수료가 커야 한다(A 1,100 sat, B 5 sat/vB는 550 sat, 50 sat/vB는 5,500 sat). 오류 문구의 나머지 부분과 `getmempoolcluster` 출력 형식은 버전에 따라 다를 수 있다.

## 퀴즈
`quiz/lesson-36.md`
