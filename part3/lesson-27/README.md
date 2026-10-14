# lesson-27 · 6-5 Taproot 스크립트 경로: 트리, 컨트롤 블록, NUMS, 6강 미니 과제

## 목표
- 스크립트 트리(TapLeaf → TapBranch → 머클 루트)가 출력키에 약속되는 과정을 설명한다.
- 스크립트 경로 witness(만족 데이터 · 리프 스크립트 · 컨트롤 블록)와 컨트롤 블록 구조를 설명한다.
- 스크립트 경로로 지출하고, 그 약속을 코드로 직접 검증한다.

## 코드
- `lib/taproot.py` — 6-5에서 더하는 부분
  - s65-code 그대로: `ser_compact(n)`, `tapleaf_hash(script, leaf_version=0xc0)`, `tapbranch_hash(a, b)`, `verify_script_path(output_xonly, script, control) -> bool` (패리티 검사는 단순화로 생략)
  - s65-tree·s65-witness·s65-nums를 코드로: `taproot_tree(tree) -> ([(리프 버전, 스크립트, 머클 경로)], 루트)`,
    `tweak_pubkey(internal_xonly, merkle_root=b"") -> (패리티, 출력키)`, `control_block(internal_xonly, leaf_version, path, merkle_root)`,
    `NUMS_H`, `nums_h()`, `p2tr_script_pubkey(output_xonly)`
- `nums_check.py` — NUMS 점 H 직접 계산 (s65-nums)
- `verify_commitment.py` — LAB ④ (s65-code) 약속 검증. 인자 없이 실행하면 노드 없는 예제
- `tapscript_lab.sh` — LAB ①~④ (s65-lab1~3 + s65-code 실행)
- `assignment/` — 6강 미니 과제 "상속형 Taproot 지갑 설계" (s6-assign)

## 실습 순서
1. **NUMS 아래 트리** 6-2의 `xpub_2.txt`, `xpub_3.txt`로 `tr(NUMS,{pk(X2/0/*),pk(X3/0/*)})`(받는용)·`/1/*`(잔돈용) → 체크섬 → 키 없는 감시 지갑 `tapscript`. 내부키가 NUMS라 키 경로로는 못 쓴다.
2. **participant_3만 서명** 1 BTC 입금 → PSBT → `decodepsbt`의 `taproot_scripts`·`taproot_bip32_derivs`(Updater가 채운 리프 두 개와 파생 경로) → participant_3 `walletprocesspsbt` → finalize → 전파. (tr() 안 miniscript·스크립트 경로 서명은 Core v26부터)
3. **witness 해부** 64B C의 Schnorr 서명 · 34B 리프 스크립트(0x20 + C x-only + OP_CHECKSIG) · 65B 컨트롤 블록(1 + NUMS 32 + B 리프 해시 32). B 리프의 내용은 체인 어디에도 없다(6-2 witness와 비교).
4. **약속 검증** 지출된 출력 scriptPubKey에서 출력키 32B(앞 0x51 0x20 제외), witness 두 번째·세 번째 항목 → `verify_script_path`가 True, 컨트롤 블록의 내부키 = NUMS.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-27/nums_check.py
python part3/lesson-27/verify_commitment.py                 # 노드 없이
bash   part3/lesson-27/tapscript_lab.sh                     # regtest, lesson-24의 xpub_2/3.txt·participant_3 지갑
```

## 기대 출력
`nums_check.py` (결정적)
```
SHA256(0x04‖G.x‖G.y) = 50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0
H.x                   = 50929b74c1a04954b78b4b6035e97a5e078a5a0f28ec96d547bfee9ace803ac0
슬라이드 값과 같음     : True
해시에서 나온 x라 누구도 H = h·G인 h를 미리 알 수 없다 → 키 경로 봉쇄
```
(해시 값이 그대로 곡선 위의 x라 lift_x가 바로 성공한다.)

`verify_commitment.py` (결정적 · B, C = 공개 테스트 니모닉 m/86h/1h/1h/0/0, m/86h/1h/2h/0/0의 x-only 키)
```
잎 해시 B 3afd85b54954af42d2c2627049dbed2f77a062694fce316e855d9dcc23e9da2c
잎 해시 C 5bccd8b9aa0763671c2ddf02cfe8ae3685eecb2d1e66ae9f361e84a275f92c71
머클 루트 04e9a44d1d973ac7f27dd24c1d161570252fe8edb9a413bc5e96e1c547e575a7 = TapBranch(작은 쪽‖큰 쪽) True
출력키 Q  c2c5b96f01c02f3d08ccce39ee08d65102d61030e8da7d3a8914da95cb151020 · 주소 bcrt1pctzmjmcpcqhn6zxvecu7uzxk2ypdvypsard86w5fzndftjc4zqsqtk4cj2

-- C 리프로 지출할 때 witness: [C의 서명 64B, 리프 스크립트, 컨트롤 블록] --
리프 스크립트 34 B: 20aa8ce86d74a1b5c968d6ae31046ac7701dc3007d13eaea3b1d4e8bf903b10bc1ac
컨트롤 블록   65 B: 버전·패리티 0xc0 · 내부키 50929b74c1a04954… · 형제 해시 ['3afd85b54954af42…']
verify_script_path: True
컨트롤 블록의 내부키 = NUMS: True
B 리프의 내용(B의 키)은 어디에도 없고 해시 32바이트로만 남는다.
```

`tapscript_lab.sh` (키·주소·서명은 실행마다 다름 · 긴 값은 줄여 적음)
```
[true,true]
{
  "taproot_scripts": [ { "script": "20…ac", "leaf_ver": 192, "control_blocks": [ "c050929b…" ] }, { … } ],
  "taproot_bip32_derivs": [ { "pubkey": "…", "master_fingerprint": "…", "path": "m/84h/1h/0h/0/0", "leaf_hashes": [ "…" ] }, { … } ]
}
e2bb6396a96d625555316dabb10b0fbaea0a485077f62c9f6b8842ada63aafa8 (실행마다 다름)
[ { "hex": "…(128자)", "bytes": 64 }, { "hex": "20…ac", "bytes": 34 }, { "hex": "c050929b74c1…", "bytes": 65 } ]
aa8ce86d74a1b5c968d6ae31046ac7701dc3007d13eaea3b1d4e8bf903b10bc1 OP_CHECKSIG (C의 x-only 키, 실행마다 다름)
리프 스크립트 34 B: 20…ac
컨트롤 블록   65 B: 버전·패리티 0xc0 또는 0xc1 · 내부키 50929b74c1a04954… · 형제 해시 ['…']
verify_script_path: True
컨트롤 블록의 내부키 = NUMS: True
```
- 컨트롤 블록 첫 바이트는 0xc0(출력키 y 짝수) 또는 0xc1(홀수) — 실행마다 다름.
- 지갑의 키가 84h 경로(wpkh 디스크립터에서 가져온 xpub)라 `taproot_bip32_derivs`의 경로도 84h다.

## 테스트
`python -m pytest tests/test_taproot.py` — BIP341 wallet-test-vectors scriptPubKey 7개 전부(잎 해시, 머클 루트, 조정값, 출력키, scriptPubKey, 주소, 컨트롤 블록), 키 경로 조정 개인키, NUMS H, 깊이별 컨트롤 블록 크기(65·97B).

## 퀴즈
`quiz/lesson-27.md`
