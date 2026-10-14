# lesson-33 · 8-2 멤풀 정책: 합의 vs 정책, 정책 항목, 더스트 실습

## 목표
- 합의 규칙과 릴레이 정책을 구분한다.
- 주요 표준성 정책과 멤풀 관리 규칙을 설명한다.
- `testmempoolaccept`로 정책 통과 여부와 거부 사유를 해석한다.

| | 합의 규칙 | 릴레이 정책 |
|---|---|---|
| 질문 | 이 트랜잭션·블록이 유효한가 | 멤풀에 넣고 이웃에 전달할 만한가 |
| 어기면 | 그 블록 전체가 무효 | 내 멤풀에 안 넣고 전달 안 함. 블록에 들어 있으면 받아들임 |
| 바꾸려면 | 소프트포크·하드포크 (11-4) | 노드 설정·버전 변경만으로 |
| 노드 간 | 모두 같아야 함 | 노드마다 다를 수 있음 |

주요 정책 항목 (Core 31 기본값, s82-items): 최소 릴레이 수수료 0.1 sat/vB(Core 30~) · 표준 크기 weight 400,000 WU · 표준 스크립트 · 더스트(5-3) · OP_RETURN 기본 100,000바이트, 여러 개 허용(Core 30~) · 클러스터당 64개·101 kvB(Core 31, 8-5).
멤풀 관리 (s82-manage): 기본 300MB(메모리 기준), 넘치면 수수료율 낮은 것부터 축출 · 기본 2주 뒤 만료 · 지갑 재전파 · 사라져도 취소가 아니다 · 채굴자 직접 제출.

## 파일
- `policy_lab.sh` — 실습 ①②③ (s82-lab1, s82-lab2)

## 실습 순서
1. `getmempoolinfo`에서 size·bytes·usage·maxmempool·mempoolminfee·minrelaytxfee를 앞 장과 대조한다.
2. bob에게 0.000001 BTC(100 sat) 출력 하나 → `fundrawtransaction` → `signrawtransactionwithwallet` → `DUST`에 저장 → `testmempoolaccept`. 기대: `allowed false`, 더스트 관련 reject-reason.
   지갑 단계(`fundrawtransaction`)에서 먼저 거부될 수도 있다 → "지갑도 정책을 미리 적용한다". 이때 스크립트는 입력과 잔돈을 직접 채워(`createrawtransaction`에 입력 지정, 수수료 1,000 sat) 같은 더스트 트랜잭션을 만들어 다음 단계로 넘어간다.
3. 금액을 0.00001(1,000 sat)로 올리면 `allowed true`.
4. 2단계의 더스트 트랜잭션을 `generateblock`으로 직접 채굴 → 블록에 정상적으로 들어간다. 합의상 유효하기 때문이다(14-1의 핵심 논거 하나).

## 실행
```bash
bash part4/lesson-33/policy_lab.sh        # regtest 노드, miner·alice·bob 지갑, jq 필요
```

## 기대 출력 (txid·hash는 실행마다 다름)
```
{
  "size": 0,
  "bytes": 0,
  "usage": 0,
  "maxmempool": 300000000,
  "mempoolminfee": 0.00000100,
  "minrelaytxfee": 0.00000100
}
```
수수료 필드의 단위는 BTC/kvB다. 0.00000100 BTC/kvB = 100 sat/kvB = 0.1 sat/vB(Core 30~ 기본값). size·bytes·usage는 멤풀 상태에 따라 다르다.

지갑이 먼저 거부한 경우 (오류 문구는 Core 버전에 따라 다를 수 있다)
```
error code: -4
error message:
Transaction amount too small
→ 지갑 단계에서 먼저 거부됐다: 지갑도 정책을 미리 적용한다. 위 오류 메시지를 읽어 보자.
  (저장소 보완) 다음 단계를 위해 입력·잔돈을 직접 채워 같은 더스트 트랜잭션을 만든다 (수수료 1,000 sat).
```
정책 검사
```
[
  {
    "txid": "5d0c…e1a2",              (실행마다 다름)
    "wtxid": "9b41…07cc",             (실행마다 다름)
    "allowed": false,
    "reject-reason": "dust"
  }
]
# 3. 금액을 0.00001(1,000 sat)로 올려 같은 과정 → allowed true
{"allowed":true,"vsize":141}          (vsize는 입력 구성에 따라 다름)
# 2단계의 더스트 트랜잭션을 직접 채굴 (채굴자 직접 제출 재현)
{
  "hash": "3f6a…9d10"                 (실행마다 다름)
}
더스트 트랜잭션 5d0c…e1a2 확인 수: 1
→ 정책으로 거부된 트랜잭션이 블록에는 정상적으로 들어간다 (합의상 유효)
```

## 토론
- 노드가 거부한 트랜잭션은 무효인가? → 정책 위반일 뿐 합의상 유효할 수 있다.
- 정책 변경도 소프트포크인가? → 아니다. 블록 유효성 규칙은 그대로다.
- 노드 정책은 전달을 막을 수는 있어도 블록 포함을 막지는 못한다(14-1).

## 퀴즈
`quiz/lesson-33.md`
