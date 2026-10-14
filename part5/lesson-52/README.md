# lesson-52 · 12-4 상속과 비상 복구, 12강 미니 과제

## 목표
- 보안과 복구 가능성 사이의 긴장 관계를 설명한다 (s124-tension).
- 상대 타임락 복구 경로가 있는 지갑을 구성하고 두 경로로 각각 지출한다 (s124-lab1~3).
- 상속 문서에 넣을 것과 넣지 말 것을 구분한다 (s124-doc).

"평소에는 나만, 내가 오래 사라지면 그때만 가족도" → 시간 조건을 수탁자 없이 스크립트로.
```
or(pk(본인), and(pk(가족), older(N)))
```
- 평시: 본인 서명만으로 언제든 지출. N블록 동안 안 움직이면 가족 키로도 지출.
- `older`는 상대 타임락(6-3) → 코인이 마지막으로 블록에 들어간 시점부터 센다.
- 운영 부담 = 리프레시: N블록 전에 코인을 자기에게 다시 보내 타이머 초기화. N ≤ 65,535블록(약 15개월), 1년 ≈ 52,560블록.
- Taproot로 구현하면 본인 키 = 내부키(키 경로), 가족 조건 = 스크립트 리프 → 평시 지출이 단일 서명과 구분되지 않는다(6-4, 6-5).

확장 패턴(s124-patterns): 단계적 복구(본인 / 6개월 후 가족 2-of-3 / 1년 후 변호사 + 가족 1), 기관 비상 키(2-of-3 평시 / 1년 미사용 시 비상 키 단독), 협업 커스터디(본인 + 서비스 / 본인 + 백업 키 / 일정 기간 후 서비스 + 백업). 정책이 복잡해질수록 지갑 소프트웨어가 그 miniscript를 서명·완성할 수 있는지 미리 리허설한다.

상속 문서(s124-doc): **위치와 절차는 쓰고, 비밀은 쓰지 않는다.**
- 넣을 것: 자산이 존재한다는 사실과 대략적 위치 · 디스크립터(공개 정보), 사용한 지갑 소프트웨어 · 단계별 복구 안내서 · 연락할 사람 · 백업 장소 목록(내용이 아니라 위치)
- 넣지 말 것: 니모닉·개인키 원문 · 패스프레이즈(별도 경로로) · 한 문서에 모든 비밀을 모으는 것
- 유언장은 집행 전에 여러 사람이 볼 수 있다 → 비밀을 넣지 않는다. 상속세·유언 효력 등 법적 절차는 이 과정의 범위 밖(전문가 상담).

## 파일
- `estate_lab.sh` — 실습 ①~④ 전체 (N = 20블록)
- `assignment/` — 12강 미니 과제 "우리 집 상속·복구 설계 1쪽" (README, 양식, 예시, 제출 전 비밀 점검 스크립트)

## 준비
`bash env/setup_regtest.sh` (miner, bob). 6-2의 `participant_1`(본인)·`participant_2`(가족) 지갑과 `xpub_1.txt`·`xpub_2.txt`. 파일이 있는 폴더에서 실행하거나 `XPUB_DIR=폴더`. 없으면 스크립트가 6-2 s62-lab1 1단계를 그대로 돌려 만든다. `jq` 필요.

## 실습 순서
① 상속 지갑 만들기 (s124-lab1)
```bash
X1=$(cat xpub_1.txt); X2=$(cat xpub_2.txt)      # 6-2: participant_1 = 본인, _2 = 가족
EXT="wsh(or_d(pk($X1/0/*),and_v(v:pk($X2/0/*),older(20))))"
INT="wsh(or_d(pk($X1/1/*),and_v(v:pk($X2/1/*),older(20))))"
EXT="$EXT#$(bitcoin-cli -regtest getdescriptorinfo "$EXT" | jq -r .checksum)"
INT="$INT#$(bitcoin-cli -regtest getdescriptorinfo "$INT" | jq -r .checksum)"
bitcoin-cli -regtest -named createwallet wallet_name=estate \
  disable_private_keys=true blank=true
bitcoin-cli -regtest -rpcwallet=estate importdescriptors "[
  {\"desc\":\"$EXT\",\"active\":true,\"internal\":false,\"timestamp\":\"now\"},
  {\"desc\":\"$INT\",\"active\":true,\"internal\":true,\"timestamp\":\"now\"}]"
bitcoin-cli -regtest -rpcwallet=miner sendtoaddress \
  $(bitcoin-cli -regtest -rpcwallet=estate getnewaddress) 1
bitcoin-cli -regtest -rpcwallet=miner -generate 1
```
② 가족이 너무 일찍 시도하면 (s124-lab2) — `sequence: 20`이 `older(20)`을 만족시키겠다는 약속. 아직 1확인뿐이라 멤풀이 거부한다.
```bash
U=$(bitcoin-cli -regtest -rpcwallet=estate listunspent | jq -c '.[0] | {txid, vout}')
TXID=$(echo $U | jq -r .txid); VOUT=$(echo $U | jq .vout)
DEST=$(bitcoin-cli -regtest -rpcwallet=bob getnewaddress)
PSBT=$(bitcoin-cli -regtest -rpcwallet=estate walletcreatefundedpsbt \
  "[{\"txid\":\"$TXID\",\"vout\":$VOUT,\"sequence\":20}]" \
  "[{\"$DEST\":0.5}]" 0 '{"add_inputs":false,"fee_rate":5}' | jq -r .psbt)
SIGNED=$(bitcoin-cli -regtest -rpcwallet=participant_2 walletprocesspsbt $PSBT | jq -r .psbt)
HEX=$(bitcoin-cli -regtest finalizepsbt $SIGNED | jq -r .hex)
bitcoin-cli -regtest sendrawtransaction $HEX      # 거부: non-BIP68-final
```
③ 20블록 후 같은 HEX가 성공 (s124-lab3)
```bash
bitcoin-cli -regtest -rpcwallet=miner -generate 20
bitcoin-cli -regtest sendrawtransaction $HEX      # 성공 → txid
```
④ 새 입금 → sequence 지정 없이 participant_1(본인)이 서명 → 즉시 전파 성공. 두 트랜잭션의 witness를 `decoderawtransaction`으로 비교한다.

한 번에: `bash part5/lesson-52/estate_lab.sh`

스크립트가 슬라이드와 다른 점: ②에서 `.[0]` 대신 ①에서 입금한 txid로 UTXO를 거른다(다시 실행해 estate에 오래된 UTXO가 있어도 ②가 반드시 "너무 이른" 시도가 되도록). ③·④ 뒤에 블록 1개를 만들어 확정한다.

## 기대 출력
txid·주소·tpub은 실행마다 다름. 이 환경에는 노드가 없어 `bash -n`·shellcheck까지만 했다(슬라이드는 Core 31.1로 직접 실행해 확인했다고 밝힌다). witness 바이트 수는 스크립트 구조로 정해진다.
```
== ② 가족이 너무 일찍 시도하면 ==
error code: -26
error message:
non-BIP68-final
→ 거부(non-BIP68-final)가 정상이다. HEX는 ③에서 다시 쓴다.
== ③ 20블록 후 같은 HEX가 성공 ==
가족 경로 txid 5d2e…(실행마다 다름)
== ④ … ==
본인 경로 txid a07c…(실행마다 다름)
== witness 비교 (decoderawtransaction) ==
본인 경로: [본인 서명] [witnessScript]
[72,76]
가족 경로: [가족 서명] [빈 값] [witnessScript]
[72,0,76]
witnessScript:
02…본인 공개키 OP_CHECKSIG OP_IFDUP OP_NOTIF 03…가족 공개키 OP_CHECKSIGVERIFY 20 OP_CHECKSEQUENCEVERIFY OP_ENDIF
```
- 서명 길이는 DER 인코딩이라 71~73바이트(대부분 72 또는 71). 공개키 앞 바이트 02/03은 실행마다 다름.
- witnessScript 76바이트 = `<본인 33B> CHECKSIG IFDUP NOTIF <가족 33B> CHECKSIGVERIFY <20> CSV ENDIF` (34+1+1+1+34+1+2+1+1). `20`은 1바이트 푸시 `01 14`.
- 가족 경로의 빈 값 = `or_d`의 왼쪽(본인 `CHECKSIG`)을 실패(0)시키고 `IFDUP NOTIF`로 오른쪽(가족 + older)을 고른다.

토론(s124-lab3): "본인이 리프레시를 잊으면?" — 본인이 멀쩡해도 가족 경로가 열린 상태가 된다. "가족 키가 해킹되면 무엇을 잃나?" — 평시에는 아무것도(타임락이 막는다). 단, 본인이 N블록 동안 움직이지 않으면 해커가 가족 경로로 가져갈 수 있다 → 리프레시가 보안 장치이기도 하다.

## 흔히 막히는 지점
- 체크섬을 붙이지 않은 디스크립터를 `importdescriptors` → 실패.
- 셸 따옴표 이스케이프 — 화면 그대로 옮겨 쓰거나 스크립트를 쓴다.
- ②의 오류에 당황 — 오류가 나야 정상이다. `HEX` 변수를 지우지 말 것(③에서 같은 HEX를 다시 보낸다).
- ③의 기준: 멤풀은 "다음 블록 높이 − 입금이 확정된 블록 높이 ≥ 20"이면 받아 준다. 입금 확정 뒤 블록을 19개 이상 만들면 되고, 슬라이드는 넉넉히 20개를 만든다. 그보다 적으면 여전히 non-BIP68-final.
- `xpub_1.txt: No such file` — 6-2를 한 폴더에서 실행하거나 `XPUB_DIR`을 준다.

## 퀴즈
`quiz/lesson-52.md`
