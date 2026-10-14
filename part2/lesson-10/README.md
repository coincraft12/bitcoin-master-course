# lesson-10 · 3-2 공개키 형식: 비압축·압축·x-only와 y 복원

## 목표
- 65B 비압축(04‖x‖y), 33B 압축(02/03‖x), 32B x-only(x, y는 짝수로 약속)의 바이트 구조를 구분한다.
- 압축 공개키에서 `y = (x³+7)^((p+1)/4) mod p`로 y를 복원하고, 곡선 위인지 확인한다.
- 같은 점이라도 형식이 다르면 주소가 달라지는 이유를 설명한다.

## 만드는 코드 (`lib/keys.py`)
`ser_uncompressed(Q)`, `ser_compressed(Q)`, `ser_xonly(Q)`, `parse_pubkey(b)` (s32-code), 그리고 저장소 보충 `parse_xonly(b)`.

## 실습 순서
1. 세 형식의 길이 65·33·32 확인
2. `parse_pubkey(ser_compressed(Q)) == Q`
3. Core `getnewaddress "" legacy` → `getaddressinfo`의 pubkey 복원 (노드 필요)
4. x좌표를 1씩 바꿔 넣어 '곡선 위의 점이 아님' 오류 빈도 보기 (대략 절반)

## 실행
```bash
python part2/lesson-10/pubkey_formats.py
python part2/lesson-10/parse_core_pubkey.py 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
bash   part2/lesson-10/core_pubkey.sh          # regtest 노드와 alice 지갑 필요
```

## 기대 출력
`pubkey_formats.py` — [개인키 1] 부분은 결정적, [새 키]와 실험 횟수는 실행마다 다름.
```
[개인키 1]
비압축 65B: 0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
압축   33B: 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
x-only 32B: 79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798

[새 키]
비압축   : 65바이트 048e7a868ed2…96ee (실행마다 다름)
압축    : 33바이트 028e7a868ed2…2aaf (실행마다 다름)
x-only: 32바이트 8e7a868ed2…2aaf (실행마다 다름)
parse_pubkey(ser_compressed(Q)) == Q : True
parse_pubkey(ser_uncompressed(Q)) == Q: True

x+1을 40번 반복: 곡선 밖 26번, 곡선 위 14번 (실행마다 다름, 대략 절반)
```
`parse_core_pubkey.py` (개인키 1의 압축 공개키, 결정적)
```
입력 길이   : 33 바이트, 접두사 02
x           : 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
y (복원)    : 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8 (짝수)
곡선 위     : True
비압축 형식 : 0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
```
`core_pubkey.sh` — 주소와 pubkey는 실행마다 다르고 `곡선 위 : True`가 나와야 한다.
```
주소   : mhhCpMw8zeoYWQMAa1XB25nvRLqWCvgy1E (실행마다 다름)
pubkey : 0291e4fd57b4fddcc888111a9332a77766e5872512504e58df063b890ad810a096 (실행마다 다름)
입력 길이   : 33 바이트, 접두사 02 (실행마다 02 또는 03)
…
곡선 위     : True
```

## 퀴즈
`quiz/lesson-10.md`
