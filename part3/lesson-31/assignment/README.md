# 3부 미니 과제: 지갑 없이 Taproot 송금 완성하기 (7-4 · s7-assign, s7-hint)

## 과제 (다섯 단계)
1. **01** Python으로 개인키 생성 → `lib/taproot.py`로 P2TR 주소 계산
2. **02** miner에서 그 주소로 0.1 BTC 송금 후 블록 생성
3. **03** `lib/tx.py`에 직렬화 함수 추가 → bob에게 보내는 서명 전 트랜잭션 (**잔돈 주의**, 5-3)
4. **04** `lib/sighash.py`로 메시지 계산 → **조정된 개인키**로 `lib/schnorr.py` 서명
5. **05** witness를 붙여 직렬화 → `testmempoolaccept` → `sendrawtransaction`

**제출**: txid, 작성한 코드, 단계별로 막힌 지점과 해결 메모. 통과하면 lib가 키 생성부터 전파까지 지갑의 핵심을 모두 갖춘다.

> 저장소의 `lib/tx.py`에는 03의 직렬화 함수(`write_varint`, `serialize_tx`)가 이미 들어 있다(정답 상태의 lib). 직접 짜 보려면 exercise 안에서 따로 작성하고 `serialize_tx`와 바이트가 같은지 비교한다.

## 힌트 (s7-hint): 조정된 개인키
```python
from lib.ec import G, N, point_mul
from lib.taproot import tagged_hash
def tweak_seckey(d0: int) -> int:
    P = point_mul(G, d0)
    d = d0 if P[1] % 2 == 0 else N - d0              # 짝수 y에 맞춤
    t = int.from_bytes(tagged_hash("TapTweak", P[0].to_bytes(32, "big")), "big")
    return (d + t) % N                                # Q의 패리티는 sign()이 처리
```
스크립트 트리가 없으므로 TapTweak에 머클 루트 없이 P.x만(BIP86). 서명 검증이 실패하면 내부키 패리티 맞춤부터 확인.

## 파일
- `exercise_taproot_send.py` — 채울 함수 네 개(`tweak_seckey`, `build_unsigned_tx`, `sign_keypath`, `finalize`). 처음엔 NotImplementedError.
- `solution/solution_taproot_send.py` — 정답. lib만 쓴다.
  - 기본(노드 없이): 고정 키(공개 테스트 니모닉 m/86h/1h/0h/0/0)와 **가짜 UTXO**로 01·03·04·05를 실제로 실행하고 자체 검증(직렬화 왕복, 서명 해시 재계산, Schnorr 검증, witness 64B, 수수료율).
  - `--node`: 새 키 → miner 입금(02) → 같은 함수로 구성·서명 → `testmempoolaccept` → `sendrawtransaction` (regtest 노드 필요, 이 환경에서는 문법·로직 검토만).

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-31/assignment/exercise_taproot_send.py               # 처음엔 NotImplementedError
python part3/lesson-31/assignment/solution/solution_taproot_send.py      # 노드 없이 끝까지
python part3/lesson-31/assignment/solution/solution_taproot_send.py --node   # regtest 노드, miner·bob 지갑
```

## 정답 기대 출력
노드 없이 (결정적, 직접 실행한 값 · aux_rand = 0x00×32로 고정)
```
01 내부키 55355ca83c973f1d97ce0e3843c85d78905af16b4dc531bc488e57212d230116
   출력키 3b82b2b2a9185315da6f80da5f06d0440d8a5e1457fa93387c2d919c86ec8786
   주소   bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg
02 (가짜 UTXO) miner가 0.1 BTC를 보냈다고 가정: d91836ec62ca3f42df0b66c608e6f7e0df307050e6ccc5ac9472a25437beaccc:0 10000000 sat
03 서명 전: 0200000001ccacbe3754a27294acc5cce6507030dfe0f7e608c6660bdf423fca62ec3618d90000000000fdffffff02404b4c00000000001600140fa17461c68ec2241a4c4a5edf799cbe2f8fb4497a484c0000000000225120d73acf6667b7850e6e00e21bb4525a2c5e2d88956a3d2c35b0bc06f4b0df01bc00000000
   출력 [(5000000, '00140fa1…'), (4999290, '5120d73a…')]
04 서명 해시 979d392bc01c2b76f984a9aab0ccd609058451c74be78b007469323d10b76c1f
   서명     9c696aa89861c93e962c0d3f2a1e77292d9dd62e8c4b73a037db167c1b97bcd102ea745508652c5fd80a6ce2255777aad598f252384402b0a4f44f4bcb02b030
05 서명된 트랜잭션: 02000000000101ccacbe3754a27294acc5cce6507030dfe0f7e608c6660bdf423fca62ec3618d90000000000fdffffff02404b4c00000000001600140fa17461c68ec2241a4c4a5edf799cbe2f8fb4497a484c0000000000225120d73acf6667b7850e6e00e21bb4525a2c5e2d88956a3d2c35b0bc06f4b0df01bc01409c696aa89861c93e962c0d3f2a1e77292d9dd62e8c4b73a037db167c1b97bcd102ea745508652c5fd80a6ce2255777aad598f252384402b0a4f44f4bcb02b03000000000
자체 검증
  직렬화 왕복                       True
  출력키 = 이전 출력 scriptPubKey     True
  서명 해시 재계산 일치                 True
  Schnorr 검증(출력키 Q)            True
  witness 1항목 64B              True
  수수료율 ≥ 5 sat/vB              True
  txid 52f3d9ca6134e26bd276da5ea3bfaab0545d9c60bf65c481acfaa7004abb0119
  wtxid a88e65040cf6d910c1b4b873c789581438e76c7828df3294006c8e19474c92af
  size 193 · weight 568 · vsize 142 · 수수료 710 sat
노드 제출은 --node 모드 (testmempoolaccept → sendrawtransaction)
```
- 01의 주소는 2부 과제(lesson-18) BIP86 regtest 첫 주소와 같다(같은 테스트 니모닉, 같은 경로).
- 03: 입력 0.1 BTC → bob 0.05 BTC(P2WPKH) + 잔돈 4,999,290 sat(새 P2TR 주소, m/86h/1h/0h/1/0). 수수료 710 sat = 5 sat/vB × 142 vB. P2TR 키 경로 서명은 언제나 64바이트라 서명 전에 vsize를 정확히 잰다.
- 같은 서명을 libsecp256k1(coincurve `PublicKeyXOnly.verify`)로도 확인했다(True).
- 가짜 UTXO라 이 hex를 노드에 보내면 `missing-inputs`로 거부된다. 실제 제출은 `--node`.

`--node` (실행마다 다름 · 모양)
```
01 개인키 WIF (regtest 전용): cV628xvqToz45dwdPmTcJ9RgEVnWMwP8dpZBGzb9LfTk3sBHFNwc (실행마다 다름)
   주소 bcrt1p8wpt9v4frpf3tkn0srd97pksgsxc5hs52lafxwru9kgeephvs7rqjeprhg (실행마다 다름)
02 받은 코인 e2bb6396a96d625555316dabb10b0fbaea0a485077f62c9f6b8842ada63aafa8:1 10000000 sat (실행마다 다름)
자체 검증
  직렬화 왕복                       True
  …(노드 없는 모드와 같은 여섯 항목이 모두 True)
  size 193 · weight 568 · vsize 142 · 수수료 710 sat
testmempoolaccept: [{'txid': '…', 'wtxid': '…', 'allowed': True, 'vsize': 142, 'fees': {'base': Decimal('0.00000710'), …}}]
sendrawtransaction → txid 52f3d9ca6134e26bd276da5ea3bfaab0545d9c60bf65c481acfaa7004abb0119 (실행마다 다름)
잔돈 개인키 WIF (regtest 전용): cVkLuddM7M5zU6KjpE4ahNPvjA4nLUwKZqJjR9eaHyPJBPnKUzCe (실행마다 다름)
```
`allowed`가 False면 `reject-reason`을 읽는다: 서명 오류(`mandatory-script-verify-flag-failed`)면 04의 조정·패리티, 수수료 오류면 03의 잔돈 계산부터.
