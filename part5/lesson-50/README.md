# lesson-50 · 12-2 하드웨어 지갑과 에어갭, 오프라인 서명 실습

## 목표
- 온라인 조회·작성(코디네이터)과 오프라인 서명(서명 기기)을 분리하는 구조를 설계한다 (s122-roles).
- 서명 기기 화면에서 확인할 항목 다섯 가지를 빠짐없이 나열한다 (s122-check).
- 에어갭의 한계와 다중 제조사 2-of-3 구성의 장점을 설명한다 (s122-airgap).

| 역할 | 하는 일 | 가진 것 |
|---|---|---|
| 온라인 지갑 (코디네이터) | 잔액 조회, PSBT 생성, 전파 | 공개 디스크립터(xpub)만 |
| 전달 매체 | USB·QR·SD카드로 PSBT 왕복 | 공개 정보만 지나간다 |
| 서명 기기 | PSBT 검증, 화면 표시, 서명 | 개인키 |

서명 전 확인 체크리스트(s122-check)
1. 받는 주소가 의도한 주소와 **전체** 일치하는가 (12-1 주소 중독)
2. 금액이 맞는가
3. 수수료가 상식적인가 (5-3 잔돈 누락, 7-4 입력 금액 검증)
4. 잔돈 출력이 내 지갑 주소인가 (기기가 파생 경로로 스스로 검증)
5. 멀티시그라면 내 키가 포함된 정확한 디스크립터를 기기에 등록해 두었는가 (등록 안 하면 잔돈 검증 불가)

에어갭이 막는 것: USB 연결을 통한 악성코드 전파·유출. 못 막는 것: 변조된 PSBT에 사람이 승인, 논스 유출(7-2), 공급망 변조. 연결 표준: HWI, Core 외부 서명기(`-signer`, `enumeratesigners`). Core 32 출시 준비판 릴리스 노트 초안에는 `exportwatchonlywallet` RPC가 예고되어 있다(31.1에는 없다).

## 파일
- `offline_signing.sh` — s122-lab 전체 (온라인 작성 → 파일 → 오프라인 확인·서명 → 파일 → 온라인 완성·전파) + 심화(받는 주소 변조 PSBT 잡아내기)
- `check_psbt.py` — 체크리스트 5개를 `decodepsbt` 출력에서 하나씩 확인. 하나라도 실패하면 종료 코드 1
- `tamper_psbt.py` — 심화: 입력·금액·잔돈은 그대로 두고 받는 주소만 바꾼 PSBT를 만든다(온라인 측이 해킹당한 상황)

## 준비
`bash env/setup_regtest.sh` (miner·alice·bob). 5-4의 `signer`(키 보유)·`watch`(키 없음) 지갑을 그대로 쓴다. 없으면 `offline_signing.sh` 0단계가 5-4 s54-lab1과 같은 방법으로 만들고, watch 잔액이 0.2 BTC 미만이면 miner가 1 BTC를 넣는다. 명령줄 JSON 도구 `jq`가 필요하다.

## 실습 순서 (슬라이드 명령)
```bash
# 온라인 측: PSBT 작성 후 파일로
BOB=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
bitcoin-cli -regtest -rpcwallet=watch walletcreatefundedpsbt '[]' \
  "[{\"$BOB\":0.1}]" 0 '{"fee_rate":5}' | jq -r .psbt > /tmp/unsigned.psbt
# 오프라인 측: 서명 전 내용 확인 → 서명
bitcoin-cli -regtest decodepsbt $(cat /tmp/unsigned.psbt) \
  | jq '{outputs: [.tx.vout[] | {value, address: .scriptPubKey.address}], fee}'
bitcoin-cli -regtest -rpcwallet=signer walletprocesspsbt $(cat /tmp/unsigned.psbt) \
  | jq -r .psbt > /tmp/signed.psbt
# 온라인 측: 완성 후 전파
HEX=$(bitcoin-cli -regtest finalizepsbt $(cat /tmp/signed.psbt) | jq -r .hex)
bitcoin-cli -regtest sendrawtransaction $HEX
```
스크립트로 한 번에: `bash part5/lesson-50/offline_signing.sh` (저장소 최상위에서). 체크리스트만 따로:
```bash
python part5/lesson-50/check_psbt.py /tmp/unsigned.psbt "$BOB" 0.1
python part5/lesson-50/tamper_psbt.py /tmp/unsigned.psbt <공격자 주소> /tmp/tampered.psbt
python part5/lesson-50/check_psbt.py /tmp/tampered.psbt "$BOB" 0.1      # 1번에서 실패해야 정상
```
실제 하드웨어 지갑이 있으면 signer 자리를 기기로 바꿔(HWI 또는 기기 앱의 PSBT 파일 가져오기) 같은 흐름을 시연한다.

## 기대 출력
값(주소, txid, 금액 끝자리)은 실행마다 다름. 이 환경에는 노드가 없어 `check_psbt.py`의 판정 로직은 가짜 decodepsbt 사전으로만 돌려 확인했다.
```
watch 잔액: 0.79999295 BTC (키 없음)   (실행마다 다름)
== 오프라인 측: 서명 전 내용 확인 → 서명 ==
{
  "outputs": [
    { "value": 0.10000000, "address": "bcrt1q…bob 주소 (실행마다 다름)" },
    { "value": 0.69998590, "address": "bcrt1q…잔돈 주소 (실행마다 다름)" }
  ],
  "fee": 0.00000705
}
[통과] 1. 받는 주소 전체 일치: vout 0 = bcrt1q… (실행마다 다름)
[통과] 2. 금액 10,000,000 sat (의도 10,000,000 sat)
[통과] 3. 입력 … − 출력 … = 수수료 705 sat, 5.0 sat/vB (상한 50 sat/vB)
[통과] 4. vout 1 bcrt1q…: 파생 경로 있음, 서명 지갑 소유 예
[통과] 5. 단일 서명 입력 — 해당 없음
→ 5개 항목 통과. 서명해도 좋다.
== 온라인 측: 완성 후 전파 ==
3f0c…txid (실행마다 다름)
== 심화: 받는 주소를 바꾼 PSBT를 확인 단계에서 잡아내기 ==
[실패] 1. 의도한 주소 bcrt1q…bob 로 가는 출력이 없다. 출력 주소: ['bcrt1q…공격자', 'bcrt1q…잔돈']
[실패] 2. 받는 출력이 없어 금액을 확인할 수 없다
[통과] 3. …
[실패] 4. vout 0 bcrt1q…공격자: 파생 경로 없음, 서명 지갑 소유 아니오
[통과] 4. vout 1 …: 파생 경로 있음, 서명 지갑 소유 예
[통과] 5. 단일 서명 입력 — 해당 없음
→ 서명하지 않는다. 온라인 측과 받는 사람에게 다른 경로로 확인한다.
→ 변조된 PSBT는 서명하지 않았다.
```
수수료 705 sat은 P2WPKH 입력 1·출력 2(141 vB) × 5 sat/vB일 때다. 출력 순서는 무작위라 받는 출력이 vout 1일 수도 있다.

## 흔히 막히는 지점
- `Wallet file not specified` — 지갑이 여러 개 로드된 상태에서 `-rpcwallet`을 빠뜨렸다. `decodepsbt`·`finalizepsbt`·`sendrawtransaction`은 지갑이 필요 없다.
- `walletprocesspsbt` 결과 `complete: false` — signer에 그 입력의 키가 없다. watch의 디스크립터가 signer에서 나온 것인지(5-4) 확인한다.
- `Insufficient funds` — watch 잔액이 부족하다. 스크립트 0단계가 채워 주지만, 직접 명령을 칠 때는 miner로 watch 주소에 입금 후 블록 1개.
- 서명 전에 `decodepsbt`를 건너뛰는 습관 — 체크리스트가 이 실습의 본론이다.

## 퀴즈
`quiz/lesson-50.md`
