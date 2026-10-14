# lesson-41 · 10-2 머클 트리

## 목표
- 트랜잭션 목록에서 머클 루트를 직접 계산한다.
- 머클 증명으로 포함 여부를 검증하고 log₂n의 이유를 설명한다.
- witness 커밋먼트와 머클 트리의 역사적 취약점(CVE-2012-2459)을 설명한다.

잎 = 각 txid(내부 바이트 순서) → 두 개씩 이어 이중 SHA256 → 홀수면 마지막을 복제 → 하나 남을 때까지. 트랜잭션 하나라도 바뀌면 루트 → 헤더 → 작업증명이 무효.
포함 증명: 잎에서 루트까지 형제 해시만 받아 차례로 합쳐 헤더 값과 비교(9-3 SPV, 6-5 Taproot 스크립트 트리와 같은 원리). 16개 → 4, 1,024개 → 10, 4,096개 → 12.
witness 커밋먼트: wtxid로 두 번째 머클 트리, 그 루트를 코인베이스 OP_RETURN에 기록 → 헤더가 witness까지 간접 약속.

## 코드
`lib/block.py` — `merkle_root(txids)` (s102-lab 왼쪽 코드 그대로). 저장소가 보탠 것: `merkle_proof(txids, index)`, `root_from_proof`, `verify_merkle_proof`, gettxoutproof 해석 `parse_merkleblock`·`extract_matches`, 증명 만들기 `build_merkleblock`.

## 파일
- `merkle_offline.py` — 블록 100,000 루트, 증명, log₂n 표, 홀수 복제 (노드 없이)
- `merkle_lab.py` — 송금 n건 + 블록 1개 후 `getblock`의 txid로 루트 비교 (s102-lab)
- `proof_lab.sh` — `gettxoutproof`·`verifytxoutproof` → `txoutproof.py`로 헤더·형제 해시 해석 (s102-lab)
- `txoutproof.py` — PROOF hex 해석. `--demo`는 블록 100,000으로 만든 증명 (노드 없이)

## 실행
```bash
python part4/lesson-41/merkle_offline.py
python part4/lesson-41/txoutproof.py --demo
python part4/lesson-41/merkle_lab.py          # regtest 노드
python part4/lesson-41/merkle_lab.py 2        # 홀수(트랜잭션 3개) 블록
bash   part4/lesson-41/proof_lab.sh
```

## 기대 출력
`merkle_offline.py` (결정적)
```
== 1. 블록 100,000 ==
  8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87
  fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4
  6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4
  e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d
계산한 루트   f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766
헤더의 루트   f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766 True
== 2. 포함 증명: 세 번째 트랜잭션(index 2) ==
  형제 0 (내부 순서) 1d0cb83721529a062d9675b98d6e5c587e4a770fc84ed00abc5a5de04568a6e9
  형제 1 (내부 순서) 15b88c5107195bf09eb9da89b83d95b3d070079a3c5c5d3d17d0dcd873fbdacc
  검증: True
  다른 위치로 속이면: False
  트랜잭션    16개 → 증명 해시 4개
  트랜잭션  1024개 → 증명 해시 10개
  트랜잭션  4096개 → 증명 해시 12개
== 3. 홀수 복제의 함정 ==
  [A, B, C]     fa435470825de273081dcc706b25514c936fa6dc80ab965ce6970d68ddd0b553
  [A, B, C, C]  fa435470825de273081dcc706b25514c936fa6dc80ab965ce6970d68ddd0b553
```
형제 0은 4번째 txid(e9a668…)를 뒤집은 것이다. 3의 두 루트가 같아서, 루트는 같고 내용이 무효(중복)인 블록으로 노드가 정상 블록을 거부하게 만들 여지가 있었다(2012년 공개, CVE-2012-2459) → 노드가 따로 검사한다. `extract_matches`도 왼쪽과 같은 오른쪽 해시를 거부한다.

`txoutproof.py --demo` (결정적)
```
앞 80바이트 = 블록 헤더 → 해시 000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506
블록의 트랜잭션 수 4 · 증명 해시 3 개 · 플래그 비트 10110000
  해시(표시 순서) ccdafb73d8dcd0173d5d5c3c9a0770d0b3953db889dab99ef05b1907518cb815
  해시(표시 순서) 6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4
  해시(표시 순서) e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d
재계산한 루트 f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766
헤더의 루트   f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766 → 일치
증명된 트랜잭션: 위치 2, txid 6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4
```
첫 해시는 왼쪽 절반(txid 0·1)의 부모, 나머지 둘은 잎이다. 플래그는 1바이트로 채워 뒤의 0000은 패딩.

`merkle_lab.py` (regtest)
```
4 True
```
`merkle_lab.py 2` → `3 True`. 멤풀에 앞 실습의 트랜잭션이 남아 있으면 개수가 더 클 수 있다(True면 된다).

`proof_lab.sh` (txid·해시는 실행마다 다름)
```
TXID=b2f9…7e10                                     (실행마다 다름)
[
  "b2f9…7e10"
]
# PROOF 앞 80바이트 = 블록 헤더 (10-1 파서로) · 형제 해시를 꺼내 루트 재계산
앞 80바이트 = 블록 헤더 → 해시 4c0d…                (실행마다 다름)
블록의 트랜잭션 수 2 · 증명 해시 2 개 · 플래그 비트 10100000
…
헤더의 루트   … → 일치
증명된 트랜잭션: 위치 1, txid b2f9…7e10
```
흔히 막히는 곳: 잎을 뒤집지 않거나 결과를 다시 뒤집지 않아 루트가 다르게 나오는 경우.

## 퀴즈
`quiz/lesson-41.md`
