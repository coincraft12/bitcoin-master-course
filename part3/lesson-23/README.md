# lesson-23 · 6-1 Script 언어: 스택 머신, opcode, P2PKH 추적, 간이 실행기

## 목표
- 잠금(scriptPubKey)·해제(scriptSig/witness) 스크립트의 실행을 스택 상태로 한 단계씩 추적한다.
- 주요 opcode를 설명하고 바이트 스크립트를 디코딩한다.
- 반복문 없는 설계의 이유(검증 비용 예측 가능성)를 설명하고 EVM과 비교한다.

## 코드
- `lib/script.py` — 이 차시에 작성하는 간이 실행기. 슬라이드 s61-code1~3 그대로:
  `OPS`, `parse_script(b) -> list`, `is_true(v)`, `run(script_sig, script_pubkey, checksig=lambda sig, pub: True, trace=True) -> bool`
  - 두 스크립트를 따로 파싱해 차례로 실행하고 스택만 이어받는다(2010년 버그 이후 규칙).
  - `OPS`에 없는 opcode는 `OP_UNKNOWN_0x..`로 디코딩되고, 실행하면 NotImplementedError (교육용 축소판).
  - `checksig`는 아직 항상 참. 7강에서 ECDSA + 서명 해시로 바꿔 끼운다(lesson-31 `checksig_p2pkh.py`).
- `trace_p2pkh.py` — P2PKH 추적, 실패 실험, 2010년 버그 재현 시도

## 실습 순서
1. `parse_script`로 바이트 스크립트를 opcode·데이터 목록으로 바꿔 본다.
2. P2PKH 송금의 scriptSig와 이전 출력 scriptPubKey를 `run`에 넣는다 → 추적표(s61-trace) 7단계와 같은 순서로 찍히는지 확인.
   - 노드 없이: 저장소의 결정적 P2PKH 지출(`data/demo_txs.json`, lib으로 만든 예제)
   - 노드에서: 3-5 T-03 레거시 지출 `data/T-03/spend_legacy.hex`(lesson-13 `measure_sizes.sh`가 만든 파일). 이전 출력은 RPC로 조회한다.
3. 실패 실험: 공개키해시 한 바이트를 바꾸면 OP_EQUALVERIFY에서 False.
4. 선택: btcdeb 같은 스크립트 디버거로 같은 스크립트를 단계 실행해 대조.

## 실행 (저장소 최상위에서)
```bash
python part3/lesson-23/trace_p2pkh.py                              # 노드 없이
python part3/lesson-23/trace_p2pkh.py data/T-03/spend_legacy.hex   # regtest 노드 (txindex=1)
```

## 기대 출력 (노드 없이 · 결정적, 직접 실행한 값)
```
scriptSig    : ['304402204f71cea7…', '02a7451395735369…']
scriptPubKey : ['OP_DUP', 'OP_HASH160', '3a2d4145a4f098523b3e8127f1da87cfc55b8e79', 'OP_EQUALVERIFY', 'OP_CHECKSIG']

-- 추적 (스택은 오른쪽이 맨 위, 각 값 앞 8자리) --
PUSH 71B        | 30440220
PUSH 33B        | 30440220 02a74513
OP_DUP          | 30440220 02a74513 02a74513
OP_HASH160      | 30440220 02a74513 3a2d4145
PUSH 20B        | 30440220 02a74513 3a2d4145 3a2d4145
OP_EQUALVERIFY  | 30440220 02a74513
OP_CHECKSIG     | 01
결과: True

-- 실패 실험: 공개키해시 한 바이트 바꾸기 --
PUSH 71B        | 30440220
PUSH 33B        | 30440220 02a74513
OP_DUP          | 30440220 02a74513 02a74513
OP_HASH160      | 30440220 02a74513 3a2d4145
PUSH 20B        | 30440220 02a74513 3a2d4145 3b2d4145
결과: False

-- 2010년 버그 재현 시도: 해제 스크립트에 <01> OP_RETURN (OP_1 대신 1바이트 push) --
PUSH 1B         | 01
결과: False
```
- 4~6단계(OP_DUP·OP_HASH160·OP_EQUALVERIFY): 가져온 공개키가 주소에 적힌 그 키인가. 7단계(OP_CHECKSIG): 그 키로 서명이 맞는가.
- 서명은 71~72바이트(DER 70~71 + sighash 1). T-03 레거시 지출로 돌리면 서명·공개키 값만 다르고 순서와 모양은 같다.
- 분리 실행이라 해제 스크립트의 OP_RETURN은 잠금 조건을 건너뛰지 못하고 그 자리에서 실패한다.

## 테스트
`python -m pytest tests/test_script.py` — 디코더, 7단계 추적, 공개키해시 변조 실패, 진짜 checksig 연결(7강 미리보기).

## 퀴즈
`quiz/lesson-23.md`
