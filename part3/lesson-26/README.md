# lesson-26 · 6-4 Taproot 키 경로: 키 조정, 출력키 계산

## 목표
- 내부키 P, 조정값 t = TaggedHash("TapTweak", P.x ‖ 머클루트), 출력키 Q = P + t·G의 관계를 설명한다.
- BIP86 출력키와 P2TR 주소를 직접 계산해 Core와 대조한다.
- 키 경로 지출이 Schnorr 서명 하나(64바이트)로 끝나는 이유를 설명한다.

## 코드
- `lib/taproot.py` — s64-code 그대로: `tagged_hash(tag, msg)`, `lift_x(x)`(짝수 y), `output_key(internal_xonly, merkle_root=b"")`.
  2부(4-3 BIP86 주소)에서 먼저 썼고, 6-5에서 트리 함수가, 7-3에서 `lift_x`의 x ≥ FIELD_P 검사가 더해진다.
- `match_wallet.py` — LAB ③ (s64-lab2) 대조 코드. 인자 없이 실행하면 BIP86 공식 벡터.
- `taproot_lab.sh` — LAB ①③④ (s64-lab1, lab2, lab3): getaddressinfo → match_wallet.py → 키 경로 지출 witness 관찰

## 실습 순서
1. **P와 Q 얻기** alice `getnewaddress "" bech32m` → `getaddressinfo`의 `desc`(`tr([지문/86h/1h/0h/0/n]내부키 64자리)#체크섬`)와 `witness_program`(출력키). 둘이 다르다 = 조정을 거쳤다.
2. **코드로 재현** desc의 64자리를 `output_key`에 → witness_program과 같은지, `segwit_addr.encode("bcrt", 1, Q)`가 `$TR`과 같은지. 대괄호 안 경로까지 복사하지 않았는지 주의.
3. **BIP86 공식 벡터** m/86'/0'/0'/0/0: P `cc8a4bc6…` → Q `a60869f0…`, 주소 `bc1p5cyx…`(4-3에서 본 주소).
4. **키 경로 지출 관찰** TR로 0.5 BTC 받고 alice `send`로 bob에게 0.4 BTC → P2TR 입력의 witness는 항목 1개 64바이트. P2WPKH 입력이 섞였다면 항목 2개(서명 71~72 + 공개키 33)와 나란히 비교.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-26/match_wallet.py                  # BIP86 공식 벡터
python part3/lesson-26/match_wallet.py <내부키 64자리>    # 내 regtest 지갑 값
bash   part3/lesson-26/taproot_lab.sh                   # regtest 노드, alice·bob·miner 지갑
```

## 기대 출력
`match_wallet.py` (결정적, BIP86 공식 벡터와 일치)
```
a60869f0dbcf1dc659c9cecbaf8050135ea9e8cdc487053f1dc6880949dc684c
bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr
t = 2ca01ed85cf6b6526f73d39a1111cd80333bfdc00ce98992859848a90a6f0258 · 출력키 y 패리티 1
```
regtest 예 (결정적): 테스트 니모닉 m/86h/1h/0h/0/0의 내부키 `55355ca83c973f1d97ce0e3843c85d78905af16b4dc531bc488e57212d230116`을 넣으면
```
3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786
bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg
t = 5752a1fc7eb3c293e00440a1f0f1c8f607037e30c92a07fb5544fe983b648d01 · 출력키 y 패리티 1
```
(2부 과제 lesson-18의 BIP86 regtest 첫 주소와 같다.)

`taproot_lab.sh` (실행마다 다름)
```
{
  "desc": "tr([8c2a4f1e/86h/1h/0h/0/0]55355ca83c973f1d97ce0e3843c85d78905af16b4dc531bc488e57212d230116)#4d7k2sjm",
  "witness_program": "3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786"
} (실행마다 다름)
3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786
bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg
t = 5752a1fc7eb3c293e00440a1f0f1c8f607037e30c92a07fb5544fe983b648d01 · 출력키 y 패리티 1
TR=bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg
{
  "txinwitness": [
    "e8b5f1c4…(128자)"
  ],
  "len": [
    64
  ]
}
```
- 첫 두 줄이 `witness_program`, `TR`과 같아야 한다(값 자체는 지갑마다 다르다).
- alice의 다른 코인이 함께 선택되면 입력이 여럿 나온다. P2TR 입력은 `len: [64]`, P2WPKH 입력은 `len: [71 또는 72, 33]`.

## 퀴즈
`quiz/lesson-26.md`
