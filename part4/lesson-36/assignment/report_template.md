# 8강 미니 과제 보고서: RBF vs CPFP (1쪽)

## 조건
- 노드: regtest, Bitcoin Core 버전: ______
- 원본 송금 두 건: alice → bob 0.1 BTC, fee_rate 1 sat/vB
- 목표 수수료율: ____ sat/vB

## 비교 표
| 방식 | 총 수수료(sat) | 총 vsize(vB) | 실효 수수료율(sat/vB) | 확정까지 필요한 트랜잭션 수 |
|---|---|---|---|---|
| RBF (bumpfee) | | | | |
| CPFP (받는 쪽 자식) | | | | |

## 관찰
- CPFP가 RBF보다 더 낸 수수료: ____ sat. 그 차이는 무엇의 크기와 같은가? (8-4 오해 장)
- RBF 후 원본 txid는 어떻게 되었나? CPFP 후 부모 txid는?

## 결론
- 보낸 사람이면: ______
- 받는 사람이면: ______

## 첨부
getmempoolentry 출력 캡처 (RBF 대체본, CPFP 부모, CPFP 자식)
