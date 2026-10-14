# lesson-35 · 8-4 CPFP와 패키지 릴레이

## 목표
- CPFP(Child Pays For Parent)로 미확정 트랜잭션을 가속하는 원리를 설명한다.
- 패키지 수수료율(합계 수수료 ÷ 합계 크기)을 계산한다.
- 패키지 릴레이가 해결하는 문제와 L2에서의 중요성을 설명한다.

자식 C는 부모 P가 블록에 들어가야만 유효하므로 채굴자는 둘을 한 덩어리로 평가한다.
- 부모가 멤풀 최소 수수료 아래면 노드가 P를 받지 않고, 자식도 갈 곳이 없다 → 미리 서명해 수수료가 고정된 L2 트랜잭션(라이트닝 강제 종료, 13-1)이 위험해진다.
- 해결: 패키지 릴레이. Core 28부터 1부모 1자식(1P1C) 패키지, `submitpackage` RPC.
- Core 31 클러스터 멤풀: 조상 점수 대신 클러스터 단위 정렬, CPFP carve-out 제거(8-5).

## 파일
- `package_feerate.py` — 패키지 수수료율 계산. 슬라이드 예제(노드 없이), `--mempool P C`(노드)
- `cpfp_lab.sh` — 실습 ①② 받는 쪽에서 가속 (s84-lab1)
- `submitpackage_lab.sh` — 실습 ③(선택) submitpackage (s84-lab2). `restart`/`restore` 하위 명령으로 노드를 다시 띄운다

## 실습 순서
1. alice → bob 0.2 BTC, `fee_rate=1` → 부모 P.
2. bob이 그 미확정 코인으로 bob의 다른 주소에 0.199 BTC, `fee_rate=30` → 자식 C. `inputs`로 그 출력만, `add_inputs:false`, `include_unsafe:true`(남이 보낸 미확정 코인 사용 허용 — 빠뜨리면 쓸 코인이 없다는 오류).
3. `getmempoolentry`로 P의 `depends`·`spentby`, fees의 base·ancestor·descendant와 Core 31의 chunk 값을 읽고 손 계산과 대조한다.
4. (선택) 노드를 `-minrelaytxfee=0.00005`(5 sat/vB)로 띄우고, 1 sat/vB 부모를 서명만 → `testmempoolaccept` 거부 → 자식은 `prevtxs`로 미전파 부모의 txid·vout·scriptPubKey·금액을 알려 주고 서명 → `submitpackage`.

## 실행
```bash
python part4/lesson-35/package_feerate.py
bash   part4/lesson-35/cpfp_lab.sh                    # regtest 노드, miner·alice·bob 지갑, jq
bash   part4/lesson-35/submitpackage_lab.sh restart   # 선택 실습: 노드 재시작(5 sat/vB)
bash   part4/lesson-35/submitpackage_lab.sh
bash   part4/lesson-35/submitpackage_lab.sh restore   # 기본 설정으로 되돌리기
```
슬라이드 s84-lab2의 `$PID`·`$PV`·`$SPK`는 정의 줄이 화면에 없다. 스크립트는 서명한 부모를 `decoderawtransaction`으로 풀어 bob 출력의 txid, vout 번호, scriptPubKey hex를 채운다(ERRATA.md).

## 기대 출력
`package_feerate.py` (결정적)
```
s84-idea: 200 sat/200 vB(1.00) + 2800 sat/100 vB(28.00) → 패키지 3000 ÷ 300 = 10.00 sat/vB
  틀린 계산: 두 수수료율의 단순 평균 = 14.5 sat/vB (크기로 가중해야 한다)
s84-lab2: 141 sat/141 vB(1.00) + 30000 sat/110 vB(272.73) → 패키지 30141 ÷ 251 = 120.08 sat/vB
  부모 단독 1.00 sat/vB < 문턱 5 sat/vB → testmempoolaccept 거부, 패키지는 약 120 sat/vB로 수락
```
자식 110 vB는 P2WPKH 입력 1·출력 1의 vsize다. 슬라이드의 "실효 수수료율 모두 120 sat/vB"와 같다.

`cpfp_lab.sh` (txid·값은 실행마다 다름)
```
P=4b0e…92d1                                         (실행마다 다름)
C=c7a3…0e5f                                         (실행마다 다름)
{
  "fees": { "base": 0.00000141, "ancestor": 0.00000141, "descendant": 0.00004371, … },
  "depends": [],
  "spentby": [ "c7a3…0e5f" ]
}
{
  "fees": { "base": 0.00004230, "ancestor": 0.00004371, "descendant": 0.00004230, … },
  "depends": [ "4b0e…92d1" ]
}
# 손 계산과 대조: 패키지 수수료율 = (부모 + 자식 수수료) ÷ (부모 + 자식 vsize)
4b0e…92d1… vsize 141 vB, base 141 sat (1.00 sat/vB), 그 밖의 fees {…}
c7a3…0e5f… vsize 141 vB, base 4230 sat (30.00 sat/vB), 그 밖의 fees {…}
손 계산: 141 sat/141 vB(1.00) + 4230 sat/141 vB(30.00) → 패키지 4371 ÷ 282 = 15.50 sat/vB
P 확인 수: 1, C 확인 수: 1
```
값은 부모·자식이 모두 P2WPKH 입력 1·출력 2(141 vB)일 때의 예다. 자식은 0.2 BTC 입력에서 0.199 BTC를 보내고 남는 약 0.001 BTC가 bob의 잔돈 출력이 된다. 부모 vsize는 alice 지갑이 고른 입력 수·유형에 따라 다르다. 부모의 descendant가 자식 수수료만큼 크게 늘어난 것을 확인한다. Core 31의 chunk 필드 이름은 `getmempoolentry` 도움말(`bitcoin-cli help getmempoolentry`)에서 확인한다.

`submitpackage_lab.sh` (선택, txid는 실행마다 다름)
```
[ { "txid": "…", "allowed": false, "reject-reason": "min relay fee not met", … } ]
PID=8f21…a7c4 PV=0 SPK=0014…                        (실행마다 다름)
{
  "package_msg": "success",
  "tx-results": { … "effective-feerate": 0.00120…, … }
}
멤풀 건수: 2
```
슬라이드 기준(Core 31.1 실측): 부모 단독은 141 vB·141 sat로 거부, 패키지는 두 트랜잭션의 실효 수수료율 모두 120 sat/vB로 수락, 멤풀 2건.

## 퀴즈
`quiz/lesson-35.md`
