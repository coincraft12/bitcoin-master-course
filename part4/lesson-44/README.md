# lesson-44 · 11-1 작업증명과 난이도 조정

## 목표
- 작업증명이 해시 퍼즐로 동작하는 원리와 시빌 공격을 막는 이유를 설명한다.
- 간이 채굴기로 난이도와 기대 시도 횟수의 관계를 측정한다.
- 2016블록 난이도 조정 공식을 계산한다.

해시 퍼즐의 세 성질: 지름길 없음 · 찾기 어렵고 검증 쉬움(10-1 check_pow) · 진척이 쌓이지 않음(무기억성 → 10분은 평균).
상위 k비트가 0이어야 하면 기대 시도 ≈ 2^k (k가 4 늘 때마다 평균 16배). 메인넷 기대 시도 = 난이도 × 2^32.

```
실제 시간 = 마지막 블록 time − 첫 블록 time
목표 시간 = 2016 × 600초 (2주)
새 타깃   = 이전 타깃 × 실제 ÷ 목표
제한      = 한 번에 최대 4배, 최소 1/4배
```
"난이도" 숫자 = 최대 타깃 ÷ 현재 타깃(높을수록 어렵다). 타깃과 방향이 반대다. 2016블록 사이 2015개 간격만 재는 특성 → time warp, 수정안은 BIP54(14-2).

## 코드
`lib/block.py` (s111-lab1 그대로)
```python
def mine(prefix76: bytes, zero_bits: int, max_tries: int = 2**32)   # (nonce, 해시, 초) 또는 None
POW_LIMIT = 0x00000000FFFF << 208          # 메인넷 최대 타깃
TWO_WEEKS = 2016 * 600
def retarget(old_target: int, actual_timespan: int) -> int
```
저장소가 보탠 것: `next_bits(old_bits, first_time, last_time)` = retarget 결과를 Core처럼 bits로 반올림(`target_to_bits`). `tests/test_block.py`가 Bitcoin Core `pow_tests.cpp`의 조정 4건(무제한·최대 타깃 상한·1/4 하한·4배 상한)과 대조한다.

## 파일
- `mine_genesis.py` — 제네시스 헤더로 슬라이드 표 재현, 메인넷 가늠, retarget 세 경우, Core 벡터 (노드 없이)
- `mine_lab.py` — s111-lab2 코드 그대로 (regtest 최신 헤더로)

## 실행
```bash
python part4/lesson-44/mine_genesis.py
python part4/lesson-44/mine_lab.py           # regtest 노드 필요
```

## 기대 출력
`mine_genesis.py` (nonce·해시·retarget은 결정적, 시간·속도는 컴퓨터마다 다름)
```
== 1. 제네시스 헤더로 채굴 (시간은 컴퓨터마다 다름) ==
 8비트 nonce=      236 hash=005ba61e89aa…    0.00s
12비트 nonce=    4,200 hash=00055472f907…    0.01s
16비트 nonce=    8,603 hash=00007cc6ec08…    0.02s
20비트 nonce=1,085,914 hash=0000073e55b8…    2.59s
== 2. 메인넷이라면 ==
기대 시도 = 132.7T × 2^32 ≈ 5.70e+23
이 컴퓨터의 파이썬 속도 ≈ 601,601 해시/초 → 약 3.0e+10 년 (실행마다 다름)
슬라이드 가정 57만 해시/초 → 약 3.2e+10 년
== 3. retarget ==
2016블록이  1주 → 타깃 ×1/2
2016블록이  4주 → 타깃 ×2
2016블록이 10주 → 타깃 ×4
Bitcoin Core pow_tests.cpp 벡터 (메인넷 파라미터, 마지막 건은 4배 상한 시험용 시각):
  높이  32256: 실제  0.85 × 2주, bits 0x1d00ffff → 0x1d00d86a (일치)
  높이   2016: 실제  1.70 × 2주, bits 0x1d00ffff → 0x1d00ffff (일치)
  높이  68544: 실제  0.24 × 2주, bits 0x1c05a3f4 → 0x1c0168fd (일치)
  높이  46368: 실제  5.00 × 2주, bits 0x1c387f6f → 0x1d00e1fd (일치)
```
1의 nonce는 슬라이드 표(236 · 4,200 · 8,603 · 1,085,914)와 같다. 비트가 4 늘 때 평균 16배지만 무작위라 들쭉날쭉하다(12→16비트는 운 좋게 빨랐다). 약 300억 년 = 3×10^10 년. 높이 2016 줄은 실제 시간이 2주보다 길어 타깃이 커져야 하지만 최대 타깃(POW_LIMIT)에 막혀 그대로다. 높이 68544는 1/4 하한, 46368은 4배 상한이 걸린 경우다.

`mine_lab.py` (regtest, 값은 실행마다 다름)
```
 8비트 nonce=      157   0.00s
12비트 nonce=     2219   0.00s
16비트 nonce=    94318   0.16s
20비트 nonce=   826735   1.98s
```

## 퀴즈
`quiz/lesson-44.md`
