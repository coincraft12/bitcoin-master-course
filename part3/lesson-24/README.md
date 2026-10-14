# lesson-24 · 6-2 멀티시그: CHECKMULTISIG, P2SH·P2WSH, 2-of-3 PSBT 실습

## 목표
- m-of-n 멀티시그의 잠금(`OP_2 <A> <B> <C> OP_3 OP_CHECKMULTISIG`)·해제(`OP_0 <서명A> <서명C>`) 구조와 NULLDUMMY(BIP147)를 설명한다.
- P2SH · P2WSH · Taproot 스크립트 경로 · Taproot 키 경로(MuSig2) 멀티시그를 비교한다.
- 디스크립터와 PSBT로 2-of-3 지갑을 만들고 지출한다(5-4에서 설명만 했던 Combiner를 처음 실제로 쓴다).

## 코드
- `multisig_lab.sh` — LAB ①~⑤ (s62-lab1, lab2, lab2b, lab3) 한 번에. Bitcoin Core 공식 멀티시그 튜토리얼과 같은 흐름.
- `multisig_script.py` — 노드 없이 2-of-3 잠금 스크립트(sortedmulti)·P2SH·P2WSH 주소를 직접 계산

## 실습 순서
1. **xpub 모으기** participant_1~3 지갑의 받는용 wpkh 디스크립터에서 `[지문/84h/1h/0h]tpub…`를 `xpub_N.txt`로 (6-5에서 다시 쓴다).
2. **디스크립터** `wsh(sortedmulti(2, X1/0/*, X2/0/*, X3/0/*))`(받는용), `/1/*`(잔돈용) + `getdescriptorinfo` 체크섬. 이 두 줄이 지갑 복구 정보 전부다(4-5).
3. **감시 지갑** 키 없는 `multisig` 지갑에 두 디스크립터를 active로 가져와 주소를 받고 miner가 2 BTC 입금.
4. **서명 둘·결합·전파** 같은 PSBT를 participant_1과 participant_3이 서로 모른 채 서명 → P1만 보면 서명 부족 → `combinepsbt` → `finalizepsbt` → 전파. participant_2는 아무것도 하지 않았다.
5. **witness 해부** `txinwitness` 4항목: [0] 빈 값(NULLDUMMY) · [1][2] 서명 · [3] witness script. `decodescript`로 풀면 `2 <키><키><키> 3 OP_CHECKMULTISIG` — 서명하지 않은 참여자의 키까지 체인에 공개됐다(6-5 Taproot 스크립트 경로와 대비).

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-24/multisig_script.py       # 노드 없이
bash   part3/lesson-24/multisig_lab.sh          # regtest 노드, miner·bob 지갑 필요
```

## 기대 출력
`multisig_script.py` (결정적, 직접 실행한 값 · 공개 테스트 니모닉 키)
```
공개키 A·B·C (참여자 순서): ['02e7ab2537…', '024ac8da64…', '02a3f27f5e…']
sortedmulti 순서         : ['024ac8da64…', '02a3f27f5e…', '02e7ab2537…']
witness script 105 B: OP_2 024ac8da… 02a3f27f… 02e7ab25… OP_3 OP_CHECKMULTISIG
P2SH  (HASH160, 20B): 2901c5fdd21104fbdfb309a30cba5e9e4b06eaa3 → 2Mvz3pNFogQCRvDngc31xCXUwfM3VB54qSF
P2WSH (SHA256, 32B) : 1f826bfaf3d1eabdea93d98940b4e257bd17d2db7f7c082b76c411eb82f1fcc3 → bcrt1qr7pxh7hn684tm65nmxy5pd8z277305km0a7qs2mkcsg7hqh3lnpsfrk7sx
키 순서를 바꿔 만든 multi()   : bcrt1qp5fehrrm2e2wjmcn6ex57qhn5pdfpvv3tyr2mqyz7xqkhr87722s2yrfvz ← 다른 주소

해제 witness 모양 (서명 A, C): [빈 값(NULLDUMMY), <서명A>, <서명C>, witness script]
서명 순서는 공개키 순서와 같아야 한다. CHECKMULTISIG는 키 목록을 앞에서부터 한 번만 훑는다.
```

`multisig_lab.sh` (지문·tpub·주소·서명·txid는 실행마다 다름 · 긴 값은 `…`로 줄여 적음)
```
[5a1b7c2e/84h/1h/0h]tpubDC…(111자) (실행마다 다름)
… (참여자 3명)
EXT=wsh(sortedmulti(2,[5a1b7c2e/84h/1h/0h]tpub…/0/*,[…]tpub…/0/*,[…]tpub…/0/*))#k8x2v5qd (실행마다 다름)
INT=wsh(sortedmulti(2,[5a1b7c2e/84h/1h/0h]tpub…/1/*,[…]tpub…/1/*,[…]tpub…/1/*))#3n7c0lh9 (실행마다 다름)
[true,true]
MS_ADDR=bcrt1qr7pxh7hn684tm65nmxy5pd8z277305km0a7qs2mkcsg7hqh3lnpsfrk7sx (실행마다 다름)
{"next":"signer"}
e2bb6396a96d625555316dabb10b0fbaea0a485077f62c9f6b8842ada63aafa8 (실행마다 다름)
[
  "",
  "3044022027dc95ad…01",
  "304402200de66acf…01",
  "5221024ac8da64…53ae"
]
2 024ac8da64… 02a3f27f5e… 02e7ab2537… 3 OP_CHECKMULTISIG
```
- `{"next":"signer"}`: participant_1의 서명 하나만으로는 부족하다. 결합 후 finalize가 돼야 전파된다.
- witness의 서명 두 개는 sortedmulti 정렬 순서(공개키 순서)대로 들어간다.

## 퀴즈
`quiz/lesson-24.md`
