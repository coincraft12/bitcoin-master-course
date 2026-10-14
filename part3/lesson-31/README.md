# lesson-31 · 7-4 Sighash와 MuSig2, 3부 미니 과제

## 목표
- sighash 유형(ALL 0x01 · NONE 0x02 · SINGLE 0x03 · ANYONECANPAY 0x80 조합 · Taproot DEFAULT 0x00)별 서명 보호 범위를 설명한다.
- 서명 해시에 입력 금액이 들어간 이유(레거시 → BIP143 서명 입력 금액 → BIP341 모든 입력 금액·scriptPubKey)를 설명한다.
- Taproot 서명 해시를 계산해 실제 서명을 검증하고, MuSig2(BIP327: 키 집계 · 2라운드 · 부분 서명 집계)를 설명한다.

## 코드
- `lib/sighash.py` — 이 차시에 작성
  - s74-code1·2 그대로: `sha(b)`, `outpoint(i)`, `ser_out(o)`, `taproot_sighash(tx, prevouts, idx, hash_type=0x00)` (키 경로·annex 없음, `prevouts = [(sat, scriptPubKey bytes)]`)
  - s74-amount의 나머지 두 방식: `bip143_sighash(tx, idx, script_code, amount, hash_type=0x01)`, `legacy_sighash(tx, idx, script_code, hash_type=0x01)`, `p2wpkh_script_code(pubkey_hash)`
- `tr1_lab.sh` — LAB ① (s74-lab1) P2TR 코인 하나짜리 지갑 tr1에서 지출 만들기 → ②③ 스크립트 실행
- `verify_keypath.py` — LAB ② (s74-lab2) 노드가 하는 Taproot 키 경로 서명 검증을 내 코드로 (`--demo`: 노드 없이)
- `scope.py` — LAB ③ (s74-lab3) DEFAULT는 출력을 고정, NONE은 백지수표 (`--demo`: 노드 없이)
- `sighash_vectors.py` — 공식 벡터: BIP341 키 경로 7개, BIP143 예제 13개, Core 레거시 500개
- `checksig_p2pkh.py` — 6-1 실행기의 checksig 자리에 진짜 검증 연결 (demo P2PKH, 블록 170 P2PK)
- `musig2/` — s74-caveat "원리 실습은 BIP327 참조 구현으로": `reference.py`·`vectors/`(bitcoin/bips 원본), `musig2_demo.py`
- `assignment/` — 3부 미니 과제 "지갑 없이 Taproot 송금" (s7-assign, s7-hint)

## 실습 순서
1. **LAB ①** tr1 지갑에 P2TR 코인 하나(0.7 BTC) → bob에게 0.3 BTC PSBT → `decodepsbt`의 `witness_utxo`를 `prevouts.json`으로 → 서명·finalize한 hex를 `tr1_spend.hex`로. 코인이 하나여야 입력이 하나로 정해진다.
2. **LAB ②** `parse_tx` → prevouts(금액은 반올림해 sat 정수) → 서명 65B면 마지막 바이트가 hash_type, 64B면 DEFAULT → `taproot_sighash` → 출력키(0x51 0x20 뒤 32B)로 7-3 `verify` → True. 출력 금액 하나를 바꾸면 False.
3. **LAB ③** DEFAULT·NONE 메시지를 저장 → 첫 출력에 1,000,000 sat 더하기 → DEFAULT는 달라지고(False) NONE은 그대로(True).
4. 공식 벡터로 확인. 값이 하나라도 다르면 바이트 순서·리틀 엔디안부터 의심.
5. MuSig2: 참조 구현 공식 벡터(`python reference.py`) → 2-of-2 데모. Core는 musig() 디스크립터 30부터, 지갑 MuSig2 서명 31부터 지원 — regtest 지출은 선택 과제.

## 실행 (저장소 최상위에서)
```bash
bash   part3/lesson-31/tr1_lab.sh                    # regtest: tr1 지갑 → verify_keypath.py → scope.py
python part3/lesson-31/verify_keypath.py --demo      # 노드 없이
python part3/lesson-31/scope.py --demo
python part3/lesson-31/sighash_vectors.py
python part3/lesson-31/checksig_p2pkh.py
python part3/lesson-31/musig2/reference.py           # BIP327 공식 벡터 (출력 없이 끝나면 통과)
python part3/lesson-31/musig2/musig2_demo.py
```

## 기대 출력 (결정적, 직접 실행한 값)
`verify_keypath.py --demo` (tr1_lab.sh에서도 같은 두 줄 — 값은 지갑마다 다르지만 True, False)
```
True
False
```
`scope.py --demo`
```
False
True
```
`sighash_vectors.py`
```
BIP341 키 경로 sigHash
  입력 0 SINGLE               2514a6272f85cfa0… True
  입력 1 SINGLE|ANYONECANPAY  325a644af47e8a5a… True
  입력 3 ALL                  bf013ea93474aa67… True
  입력 4 DEFAULT              4f900a0bae3f1446… True
  입력 6 NONE                 15f25c298eb5cdc7… True
  입력 7 NONE|ANYONECANPAY    cd292de50313804d… True
  입력 8 ALL|ANYONECANPAY     cccb739eca6c13a8… True
BIP143 예제 sigHash 일치 13/13
레거시 sighash.json 일치 500/500
```
`checksig_p2pkh.py`
```
== ① demo P2PKH: 진짜 checksig ==
PUSH 71B        | 30440220
PUSH 33B        | 30440220 02a74513
OP_DUP          | 30440220 02a74513 02a74513
OP_HASH160      | 30440220 02a74513 3a2d4145
PUSH 20B        | 30440220 02a74513 3a2d4145 3a2d4145
OP_EQUALVERIFY  | 30440220 02a74513
OP_CHECKSIG     | 01
결과: True
출력 금액 1 sat 변조 후: False

== ② 블록 170 (P2PK) ==
PUSH 71B        | 30440220
PUSH 65B        | 30440220 0411db93
OP_CHECKSIG     | 01
결과: True
```
②는 2009년 1월 사토시가 할 피니에게 보낸 송금의 서명을, 블록 9 코인베이스 출력(P2PK)의 공개키로 우리 lib이 처음부터 검증한 결과다.

`musig2/musig2_demo.py` (고정 키·고정 논스 rand — 실제로는 서명마다 새 난수)
```
참여자 공개키 : 02525bf99a7a3ecaff… 03a2486cd2f03ac660…
집계 x-only 키: c31906562ed8c28416e4e635d1e7afe65b77cebf7b7fa30aad26554a78328617
출력키 Q      : 8b88b803471fb5b3cf4b84a7a7a2fd1dd8af6676cdc6c050d2af530a7e153f77 · 주소 bcrt1p3wytsq68r76m8n6tsjn60gharhv27enkehrvq5xj4afs5ls48amskfzzpy
부분 서명 검증: True True
집계 서명 64B : 04b6847a7571b73c95a9b17e83fb28eb3b168a7632ab643bea5e03328216cbf8184d6f21ba349e794f756ee28708445dba1f7c67f90d7963db841e10572e6a53
lib/schnorr.verify(msg, Q, sig): True
→ 키 경로 witness는 [64B 서명] 하나. 단일 서명 지갑과 구분할 수 없다 (6-4).

6강 과제의 자리표시 키를 이 집계키로 바꾸면 (복구 키는 그대로):
  tr(c31906562ed8c28416e4e635d1e7afe65b77cebf7b7fa30aad26554a78328617,and_v(v:pk(340404d6ca0d8a9b019d3ac3527ad2ac063c60446fdd13e76c0d2e5704c10163),older(52560)))#ngd4yncf
  주소 bcrt1pq2t6zfyp7y84asrykstt9q4yn8zj4396yndddk4p3338tj6wcn5s22gdne
```
- 집계 서명은 출력키 Q에 대한 보통의 BIP340 서명이라 7-3의 `lib/schnorr.verify`가 그대로 통과시킨다 = 단일 서명 지갑과 구분할 수 없다.
- 마지막 두 줄은 6강 미니 과제(lesson-27)의 자리표시 키를 이 집계키로 바꾼 디스크립터·주소다(12-4 상속 설계로 이어진다).

`tr1_lab.sh` (실행마다 다름)
```
[
  {
    "amount": 0.70000000,
    "scriptPubKey": {
      "asm": "1 3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786",
      "desc": "rawtr(3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786)#…",
      "hex": "51203b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786",
      "address": "bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg",
      "type": "witness_v1_taproot"
    }
  }
] (실행마다 다름)
True
False
False
True
```

## 테스트
`python -m pytest tests/test_sighash.py tests/test_script.py` — 레거시 500 · BIP143 13(서명 ECDSA 검증 포함) · BIP341 7(공식 witness 서명 검증 포함), 블록 170 서명, 범위 체감, 진짜 checksig.

## 퀴즈
`quiz/lesson-31.md`
