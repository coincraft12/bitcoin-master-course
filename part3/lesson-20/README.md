# lesson-20 · 5-2 직렬화와 witness: CompactSize, 가변성, txid·wtxid, weight·vsize, 파서

## 목표
- 레거시와 SegWit(BIP141·BIP144) 직렬화를 바이트 단위로 구분한다.
- txid(witness 제외)와 wtxid(witness 포함)의 차이, 가변성이 해결된 원리를 설명한다.
- weight = base×3 + total, vsize = ⌈weight/4⌉을 직접 계산하고 Core와 대조한다.

## 코드
- `lib/tx.py` — 이 차시에 작성하는 파서. 슬라이드 s52-code1~3 그대로:
  `dsha256(b)`, `read_varint(b, i) -> (값, 다음 위치)`, `parse_tx(hexstr) -> dict`
  (반환: `version, segwit, vin, vout, locktime, txid, wtxid, size, weight, vsize` — `size`는 s52-verify가 쓰는 값이라 함께 돌려준다. ERRATA 참고)
- `t03_segwit.sh` — LAB ① (s52-lab1) miner → alice 0.3 BTC 송금, hex를 `t03_segwit.hex`로 저장
- `verify_with_core.py` — LAB ③ (s52-verify) 다섯 항목(txid, wtxid↔hash, size, vsize, weight) 대조
- `parse_demo.py` — 노드 없이 파서를 돌려 보는 예제 (레거시 T-02, SegWit 예제 두 개)

## 실습 순서
1. `t03_segwit.sh`로 SegWit 송금을 만들고 hex를 저장한다(미확정이라 txindex 없이 조회).
2. 라이브 코딩: `read_varint` → `parse_tx` 앞부분(헤더·입력) → 뒷부분(출력·witness·ID)을 하나씩 작성하며 실행해 본다. 흔한 실수는 이전 txid 32바이트를 뒤집지 않는 것.
3. `verify_with_core.py`로 Core와 대조 → 다섯 항목 모두 True. txid가 틀리면 바이트 뒤집기·stripped 조립을, vsize가 틀리면 올림을 의심한다.
4. 같은 스크립트를 `data/T-02.hex`(레거시)에 돌려 txid = wtxid를 확인한다.

## 실행 (저장소 최상위에서)
```bash
bash   part3/lesson-20/t03_segwit.sh
python part3/lesson-20/verify_with_core.py                  # ./t03_segwit.hex
python part3/lesson-20/verify_with_core.py data/T-02.hex    # 레거시
python part3/lesson-20/parse_demo.py                        # 노드 없이
```

## 기대 출력
`verify_with_core.py` (t03_segwit.hex) — 다섯 항목 모두 True. 값은 실행마다 다름 (P2WPKH 1입력 2출력이면 vsize 141 전후).
아래 값은 같은 모양의 demo P2WPKH 지출을 넣었을 때의 실제 값이다.
```
txid True 7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95 (실행마다 다름)
wtxid True 60d18cf6826ed5f2848de6562a288e319eed7c99c2e082acd425aded3e73e0b9 (실행마다 다름)
size True 223 (실행마다 다름)
vsize True 141 (실행마다 다름)
weight True 562 (실행마다 다름)
```
`verify_with_core.py data/T-02.hex` (결정적)
```
txid True f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
wtxid True f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
size True 275
vsize True 275
weight True 1100
```
`parse_demo.py` (결정적, 직접 실행한 값)
```
== T-02 블록 170 (레거시) ==
version 1 · segwit False · 입력 1 · 출력 2 · locktime 0
  vin[0] 0437cd7f8525ceed…:0 scriptSig 72B
  vout[0] 1,000,000,000 sat · scriptPubKey 4104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac
  vout[1] 4,000,000,000 sat · scriptPubKey 410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac
txid   f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
wtxid  f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16  (txid와 같음: True)
size 275 · base 275 · weight 275×3+275 = 1100 · vsize 275

== demo P2WPKH 지출 (SegWit v0) ==
version 2 · segwit True · 입력 1 · 출력 2 · locktime 0
  vin[0] 9d68e5fe3217cca5…:0 scriptSig 0B · witness 2개 [72, 33]B
  vout[0] 9,000,000 sat · scriptPubKey 00140fa17461c68ec2241a4c4a5edf799cbe2f8fb449
  vout[1] 999,295 sat · scriptPubKey 00142f34aa1cf00a53b055a291a03a7d45f0a6988b52
txid   7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95
wtxid  60d18cf6826ed5f2848de6562a288e319eed7c99c2e082acd425aded3e73e0b9  (txid와 같음: False)
size 223 · base 113 · weight 113×3+223 = 562 · vsize 141

== BIP143 Native P2WPKH 예제 (P2PK 입력 + P2WPKH 입력) ==
version 1 · segwit True · 입력 2 · 출력 2 · locktime 17
  vin[0] 9f96ade4b41d5433…:0 scriptSig 73B · witness 0개 []B
  vin[1] 8ac60eb9575db5b2…:1 scriptSig 0B · witness 2개 [71, 33]B
  vout[0] 112,340,000 sat · scriptPubKey 76a9148280b37df378db99f66f85c95a783a76ac7a6d5988ac
  vout[1] 223,450,000 sat · scriptPubKey 76a9143bde42dbee7e4dbe6a21b2d50ce2f0167faa815988ac
txid   e8151a2af31c368a35053ddd4bdb285a8595c769a3ad83e0fa02314a602d4609
wtxid  c36c38370907df2324d9ce9d149d191192f338b37665a82e78e76a12c909b762  (txid와 같음: False)
size 343 · base 233 · weight 233×3+343 = 1042 · vsize 261
```
- P2WPKH witness는 항목 2개(서명 71~72B, 공개키 33B). witness 바이트는 가중치 1이라 base 113B인 트랜잭션의 vsize가 141이다.
- 슬라이드 계산 예(s52-weight): base 110 · total 222 → 552 WU → 138 vB. 퀴즈: base 200 · total 300 → 900 WU → 225 vB. (`tests/test_tx.py`)
- demo 예제는 공개 테스트 니모닉 키와 가짜 UTXO로 lib이 만든 결정적 트랜잭션이다(`data/make_demo_txs.py`).

## 테스트
`python -m pytest tests/test_tx.py` — T-02 txid·크기, Core sighash.json의 raw 트랜잭션 500개 파싱→직렬화 왕복,
BIP143 서명 전·후 트랜잭션의 txid 관계, BIP341 트랜잭션에 공식 witness를 붙여도 txid가 그대로인지.

## 퀴즈
`quiz/lesson-20.md`
