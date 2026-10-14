# lesson-40 · 10-1 블록 헤더

## 목표
- 블록 헤더 80바이트의 여섯 필드를 해석한다.
- bits에서 타깃을 복원하고 작업증명을 직접 검증한다.
- 이전 블록 해시가 과거 변경을 어렵게 만드는 원리를 설명한다.

| 필드 | 크기 | 의미 |
|---|---|---|
| version | 4 | 블록 버전. 소프트포크 신호 비트로도 사용 (11-5) |
| prev_block_hash | 32 | 이전 블록 헤더의 해시. 사슬을 만드는 연결고리 |
| merkle_root | 32 | 블록 안 모든 트랜잭션의 머클 루트 (10-2) |
| time | 4 | 채굴자가 적은 유닉스 시간 (허용 범위 규칙) |
| bits | 4 | 타깃의 압축 표기 |
| nonce | 4 | 채굴자가 바꿔 가며 시도하는 값 (11-1) |

모든 정수 필드는 리틀 엔디안. 블록 해시 = SHA256(SHA256(헤더 80바이트)), 표시할 때 바이트를 뒤집는다. 블록 어디에도 저장되지 않고 다음 블록의 prev로만 기록된다.
타깃 = 가수 × 256^(지수 − 3) (지수 = bits 최상위 바이트, 가수 = 하위 3바이트). 유효한 블록: int(블록 해시) ≤ 타깃.

## 코드
`lib/block.py` (s101-lab 왼쪽 코드 그대로)
```python
def parse_header(h: bytes) -> dict          # version, prev, merkle_root, time, bits, nonce, hash
def bits_to_target(bits: int) -> int
def check_pow(h: bytes) -> bool
```
저장소가 보탠 것: `serialize_header(fields)`(parse_header의 역), `header_hash(h)`, `target_to_bits(target)`(Core GetCompact), `difficulty(bits)`, `block_work(bits)`. 자세한 목록은 `lib/API.md`.

## 파일
- `header_lab.py` — s101-lab 오른쪽 코드 + 제네시스 확인 (regtest 노드)
- `genesis_header.py` — 메인넷·regtest 제네시스 헤더 해석, 타깃 비교, 변경 저항 (노드 없이)

## 실행
```bash
python part4/lesson-40/genesis_header.py
python part4/lesson-40/header_lab.py        # regtest 노드 필요
python -m pytest tests/test_block.py -q
```

## 기대 출력
`genesis_header.py` (결정적)
```
== main 제네시스 (80바이트) ==
version 1 · time 1231006505 · bits 0x1d00ffff · nonce 2083236893
prev        0000000000000000000000000000000000000000000000000000000000000000
merkle_root 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
hash        000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
target      00000000ffff0000000000000000000000000000000000000000000000000000
check_pow True · 타깃 비트 길이 224 · 난이도 1
== regtest 제네시스 (80바이트) ==
version 1 · time 1296688602 · bits 0x207fffff · nonce 2
prev        0000000000000000000000000000000000000000000000000000000000000000
merkle_root 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
hash        0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206
target      7fffff0000000000000000000000000000000000000000000000000000000000
check_pow True · 타깃 비트 길이 255 · 난이도 4.66e-10
== 변경 저항: 메인넷 제네시스의 머클 루트 1바이트를 바꾸면 ==
hash        143cf106bd17eeabb234b600818ca7e49020f993a472d51076b47823c2105d30
check_pow False → 다시 채굴해야 하고, 다음 블록의 prev_block_hash와도 맞지 않는다
```
regtest 타깃 0x7fffff00…00은 거의 최댓값이라 해시 절반 정도가 통과한다 → regtest 채굴이 즉시 끝나는 이유. 메인넷 난이도 1 타깃은 앞에 0이 32비트 붙는다.

`header_lab.py` (해시·시간은 실행마다 다름)
```
True True 0x7fffff0000000000000000000000000000000000000000000000000000000000
True
제네시스: True True True
최신 헤더 필드: {'version': '0x20000000', 'prev': '5a1c…', 'merkle_root': '9e07…', 'time': 1791974400, 'bits': '0x207fffff', 'nonce': 1, 'hash': '3b8e…'}   (실행마다 다름)
```
version은 regtest 높이에 따라 0x20000000 또는 0x30000000이다(시험용 배포 testdummy의 신호 비트 28, 11-5 lesson-48). 흔히 막히는 곳: 바이트 뒤집기를 빠뜨려 해시 비교가 False로 나오는 경우. 메인넷 노드가 있다면 최신 블록 타깃과 regtest 타깃의 자릿수를 비교해 본다.

## 퀴즈
`quiz/lesson-40.md`
