# lesson-22 · 5-4 PSBT: 역할 분리, 워치온리·서명 지갑 실습, 5강 미니 과제

## 목표
- PSBT(BIP174)의 여섯 역할(Creator · Updater · Signer · Combiner · Finalizer · Extractor) 분리 구조를 설명한다.
- 서명기가 안전하게 서명하는 데 필요한 정보(이전 출력의 금액·스크립트, 파생 경로와 지문, 잔돈 소유 정보)를 설명한다.
- 워치온리 지갑(watch)과 서명 지갑(signer)을 나눠 PSBT로 송금한다.

## 코드
- `psbt_lab.sh` — LAB ①~⑥ (s54-lab1~3) 한 번에. signer(키 있음 = 오프라인 서명기 역할)와 watch(키 없음 = 온라인 지갑 역할).
- `assignment/` — 5강 미니 과제 "세 유형 송금 비교표" (s5-assign).

## 실습 순서
1. **지갑 두 개** signer는 일반 지갑, watch는 `disable_private_keys=true blank=true`.
2. **디스크립터 옮기기** signer `listdescriptors`(기본은 공개 디스크립터)에서 wpkh 받는용(internal false)·잔돈용(internal true)을 watch에 `importdescriptors`. 두 지갑의 `getnewaddress`가 같은 주소인지 확인(xpub만으로 파생, 4-2).
3. **입금** watch 주소로 miner가 1 BTC → `getbalances`에 1 BTC: 키는 없지만 잔액은 안다. (Core 31의 디스크립터 지갑은 이 금액을 `watchonly`가 아니라 `mine`에 보여 준다 — ERRATA s54-lab1)
4. **Creator + Updater (watch)** `walletcreatefundedpsbt '[]' '[{BOB:0.2}]' 0 '{"fee_rate":5}'` → `decodepsbt`로 witness_utxo(이전 출력 금액·스크립트), bip32_derivs(지문·경로), fee 확인. `analyzepsbt`의 next = signer.
5. **Signer + Finalizer (signer)** `walletprocesspsbt` → next = extractor.
6. **Extractor (watch 쪽)** `finalizepsbt`로 hex → `sendrawtransaction` → 블록 1개.
7. 심화(선택): 4단계 PSBT(`psbt_unsigned.b64`로 남겨 둠)의 받는 주소를 서명 전에 바꾼 PSBT를 만들어 `decodepsbt` 결과를 원본과 비교 → 서명기 자체 화면에서 주소·금액·수수료·잔돈 소유를 확인해야 하는 이유. (PSBTv2·BIP370은 Core가 아직 만들지 않아 실습은 v0)

## 실행 (저장소 최상위에서)
```bash
bash part3/lesson-22/psbt_lab.sh      # regtest 노드, miner·bob 지갑 필요
```

## 기대 출력 (주소·지문·txid는 실행마다 다름)
```
{ "desc": "wpkh([d34db33f/84h/1h/0h]tpubDC…/0/*)#…", "timestamp": …, "active": true, "internal": false, … } (실행마다 다름)
{ "desc": "wpkh([d34db33f/84h/1h/0h]tpubDC…/1/*)#…", … "internal": true, … } (실행마다 다름)
[true,true]
signer 주소: bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk (실행마다 다름)
watch  주소: bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk   ← 같아야 한다 (xpub만으로 파생, 4-2)
{"mine":{"trusted":1.00000000,"untrusted_pending":0.00000000,"immature":0.00000000},"lastprocessedblock":{"hash":"…","height":…}} (높이·해시는 실행마다 다름)
{
  "inputs": [ { "amount": 1.00000000, "scriptPubKey": { "hex": "0014…", "type": "witness_v0_keyhash", … } } ],
  "fee": 0.00000705
}
[{"master_fingerprint":"d34db33f","path":"m/84h/1h/0h/0/1"}]
{"next":"signer"}
{"next":"extractor"}
7b87d541dde616f839ccc25fed8e3b6881e84109e6e1ef69713c9d5896aa0a95 (실행마다 다름)
```
- `next`가 signer → extractor로 바뀌는 것이 핵심이다. 여전히 signer라면 signer 지갑의 디스크립터와 PSBT 변수를 확인한다.
- 슬라이드의 "watchonly에 1 BTC"는 레거시 지갑 시절 표시다. 레거시 지갑이 없어진 Core 30 이후 디스크립터 지갑에는 `watchonly` 항목이 없고, 키가 없어도 지갑 디스크립터에 속한 코인은 `mine`으로 센다.
- 5 sat/vB · P2WPKH 1입력 2출력이면 fee는 705 sat 전후(141 vB × 5).

## 퀴즈
`quiz/lesson-22.md`
