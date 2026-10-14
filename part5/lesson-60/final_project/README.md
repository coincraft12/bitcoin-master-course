# 최종 프로젝트: signet에서 Taproot 볼트 지갑 구성과 운영 (14-4 · s14-final)

| 단계 | 내용 | 관련 |
|---|---|---|
| 01 설계 | 키 경로는 2-of-2 MuSig2(Core 31부터 지갑 서명 지원) 또는 단일 키, 스크립트 경로에 2-of-3 CHECKSIGADD 리프와 타임락 복구 리프 | 6-2, 6-5, 7-4, 12-4 |
| 02 디스크립터 | 디스크립터를 작성해 워치온리 지갑에 가져와 주소 생성 | 4-4 |
| 03 운영 | signet 파우셋으로 입금, PSBT로 서명을 모아 송금 | 5-4 |
| 04 설계서 | 위협 모델, 키 보관 계획, 복구 절차, 리프 배치 이유 | 12-1, 12-3, 6-5 |

| 제출물 | 평가 기준 |
|---|---|
| 디스크립터(공개) · 송금 txid · 설계서 2~3쪽 | 디스크립터 정확성 40% · 복구 경로 설계의 타당성 30% · 트랜잭션 구조 설명 30% |

> **실제 자금용 키나 니모닉은 절대 제출하지 않는다.** signet은 실제 가치가 없는 테스트 네트워크다.

## 파일
`exercise/`
- `exercise_vault_descriptor.py` — 볼트 디스크립터 문자열과 복구 리프 스크립트를 만드는 함수 두 개를 채운다. 실행하면 풀이와 대조한다
- `design_doc_template.md` — 설계서 2~3쪽 양식 (제출물, 위협 모델, 키 보관, 리프 배치 이유, 복구 절차, 트랜잭션 구조)

`solution/`
- `vault_descriptor.py` — 디스크립터 작성(체크섬 포함)과 노드 없는 주소 계산. `selftest`로 BIP386·BIP387 공식 tr() 테스트 벡터와 대조
- `vault_wallet.sh` — 01~03을 Core로 끝까지: 키 지갑 5개 → 디스크립터(파이썬과 Core 체크섬 대조) → 워치온리 지갑 → 주소(파이썬 계산과 대조) → 입금 → 키 경로 송금, 2-of-3 리프 송금, (regtest) 복구 리프 송금 → 제출물 메모
- `design_doc_example.md` — 설계서 작성 예시
- `descriptors.py` — Bitcoin Core 테스트 프레임워크의 디스크립터 체크섬 코드 원본 그대로 (https://raw.githubusercontent.com/bitcoin/bitcoin/master/test/functional/test_framework/descriptors.py, MIT, sha256 8c2a4490c1b2a09c6c6e209eda090b160214d8156e20d6db671459cb4090a16a)
- `tr_vectors.json` — BIP386·BIP387 문서 "Test Vectors" 절의 유효 디스크립터와 scriptPubKey를 정규식으로 추출 (https://raw.githubusercontent.com/bitcoin/bips/master/bip-0386.mediawiki · bip-0387.mediawiki, 원문 sha256은 파일 안에)

## 설계 (풀이가 쓰는 모양)
```
tr(K0/0/*, { multi_a(2,K1/0/*,K2/0/*,K3/0/*), and_v(v:pk(R/0/*),older(N)) })      # 키 경로 단일 키
tr(musig(K1,K2)/0/*, { multi_a(2,K1/0/*,K2/0/*,K3/0/*), and_v(v:pk(R/0/*),older(N)) })   # MUSIG=1
```
K는 각 지갑 `listdescriptors`의 받는용 `tr()`에서 뽑은 `[지문/86h/1h/계정h]tpub…`. 받는용 `/0/*`, 잔돈용 `/1/*`.

## 실행 (저장소 최상위에서)
```bash
python part5/lesson-60/final_project/solution/vault_descriptor.py selftest     # 노드 없이
python part5/lesson-60/final_project/solution/vault_descriptor.py demo         # 노드 없이, 공개 테스트 니모닉으로
bash   part5/lesson-60/final_project/solution/vault_wallet.sh                  # regtest 리허설 (N=20)
OLDER=144 NETWORK=signet bash part5/lesson-60/final_project/solution/vault_wallet.sh   # 제출용: signet
MUSIG=1 bash part5/lesson-60/final_project/solution/vault_wallet.sh            # 키 경로를 MuSig2로
python part5/lesson-60/final_project/exercise/exercise_vault_descriptor.py     # 과제 (처음엔 NotImplementedError)
```
signet: `bitcoind -signet -daemon`으로 동기화를 마친 뒤 실행한다. 스크립트가 주소를 보여 주면 signet 파우셋에서 그 주소로 입금하고, 스크립트는 확인될 때까지 30초마다 기다린다. 이후 송금도 확인을 기다린다(블록 약 10분). 복구 리프는 N블록 뒤에 같은 방법으로 쓴다 — 설계서에 절차를 적는다.

## 기대 출력
`selftest` (결정적, 직접 실행해 확인)
```
BIP386·BIP387 tr() 테스트 벡터 scriptPubKey 17/17 일치
```
`demo` (결정적, 직접 실행해 확인. 키는 공개 테스트 니모닉 abandon ×11 + about의 m/86h/1h/0h~4h — 실제 자금용 아님. 디스크립터 두 줄은 길어서 줄였다)
```
소유자(키 경로)      m/86h/1h/0h  tpubDDfvzhdVV4unsoKt…
K1             m/86h/1h/1h  tpubDDfvzhdVV4unxTr3…
K2             m/86h/1h/2h  tpubDDfvzhdVV4unz2Y7…
K3             m/86h/1h/3h  tpubDDfvzhdVV4uo2qP9…
복구 R           m/86h/1h/4h  tpubDDfvzhdVV4uo4VbF…
받는용 EXT: tr([73c5da0a/86h/1h/0h]tpubDDfvzhdVV4unsoKt5aE6…/0/*,{multi_a(2,…),and_v(v:pk(…),older(20))})#5pq8ccga
잔돈용 INT: tr([73c5da0a/86h/1h/0h]tpubDDfvzhdVV4unsoKt5aE6…/1/*,{multi_a(2,…),and_v(v:pk(…),older(20))})#9vuzgmsj
리프 (깊이, 바이트, 스크립트 hex):
  1  104B  20340404d6ca0d8a9b019d3ac3527ad2ac063c60446fdd13e76c0d2e5704c10163ac20aa8ce86d74a1b5c968d6ae31046ac7701dc3007d13eaea3b1d4e8bf903b10bc1ba20525f7ad3f2c2e9376e944a87e1aca11bef17d59c88a311322db0bdb10e49e292ba529c
  1   37B  20d39a0d56e0c6c823b1241ae452b7bb66d15cd2dde38e3807538282b140af12e7ad0114b2
받는 주소 처음 2개 (regtest):
  /0/0  bcrt1phngwcg743yd9c3z6pyafe3w7fz20xtp50ajzgtfjrfskflc4urjshlgqjj
  /0/1  bcrt1pt6933uszwcy3n5ygas4yajk5jayraxxg9yyl6u0mqysuwk0tfr9q8r8mpa
```
리프 1 끝의 `52 9c` = OP_2 OP_NUMEQUAL, 리프 2 끝의 `01 14 b2` = 20 푸시 + OP_CHECKSEQUENCEVERIFY. 계산기는 BIP386·387 벡터로 확인했지만, 이 볼트 디스크립터 자체를 Core에 넣어 본 것은 아니다(작성 환경에 노드 없음). `vault_wallet.sh`가 Core 주소와 이 계산을 대조한다.

`vault_wallet.sh` (regtest, 값은 실행마다 다름 · 노드가 없어 실행 검증하지 못했다. witness 바이트 수는 스크립트 구조로 정해진다)
```
== 01 키 5개 (서로 다른 지갑 = 서로 다른 장비라고 가정) ==
EXT=tr([지문/86h/1h/0h]tpub…/0/*,{multi_a(2,…),and_v(v:pk(…),older(20))})#체크섬   (실행마다 다름)
== 02 워치온리 지갑에 가져와 주소 생성 ==
[true,true]
Core 주소      : bcrt1p…   (실행마다 다름)
파이썬 계산 /0/0: bcrt1p…   (같아야 한다)
== 03 입금 ==
입금 txid 7b1e…   (실행마다 다름)
== PSBT로 서명을 모아 송금 ==
키 경로 (소유자 단독) txid …  witness 바이트 [64] (실제: 키 경로)
스크립트 경로 2-of-3 (K1+K3) txid …  witness 바이트 [64,0,64,104,65] (실제: 스크립트 경로)
== 복구 경로 리허설: 20블록 미사용 후 R 단독 ==
복구 경로 (R, sequence 20) txid …  witness 바이트 [64,37,65] (실제: 스크립트 경로)
제출물 메모: /tmp/vault_regtest_20_m0.txt (공개 정보만. 개인키·니모닉은 넣지 않는다)
```
- `[64,0,64,104,65]`: K3 서명, K2 자리 빈 값, K1 서명(스택 맨 위), 리프 스크립트 104B, 컨트롤 블록 65B(1 + 내부키 32 + 복구 리프 해시 32).
- `MUSIG=1`: K1·K2 지갑은 키 경로(MuSig2)와 2-of-3 리프 모두에 키가 있다. 지갑이 리프 서명까지 만들어 두면 Finalizer가 스크립트 경로로 완성할 수 있다 — 출력의 "(실제: …)"로 어느 경로로 쓰였는지 확인하고 설계서에 설명한다(트랜잭션 구조 설명 30%).

## 흔히 막히는 지점
- 디스크립터 체크섬과 키 경로 표기 — 체크섬은 `getdescriptorinfo`(또는 `vault_descriptor.py`)로, 경로는 `[지문/86h/1h/0h]tpub…/0/*`처럼 출처·확장 키·자식 경로 순서. `h`와 `'`는 같은 뜻이지만 체크섬은 문자 그대로 계산되므로 섞어 쓰면 체크섬이 달라진다.
- `multi_a`의 같은 키 중복 금지 — 참여자마다 다른 지갑.
- 복구 리프 송금이 `non-BIP68-final` — 입력 sequence를 N으로 주었는지, 입금 확정 뒤 N블록이 지났는지(12-4).
- `walletprocesspsbt` 결과 `complete:false`는 정상(정족수 미달). `combinepsbt` 뒤 `finalizepsbt`에서 완성된다. 완성이 안 되면 `analyzepsbt`로 누가 더 서명해야 하는지 본다.
- signet 지갑에 잔액이 안 보임 — 노드가 아직 동기화 중이거나, 파우셋이 다른 주소로 보냈다. `getblockchaininfo`의 `initialblockdownload`를 확인한다.
