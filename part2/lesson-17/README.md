# lesson-17 · 4-4 출력 디스크립터와 miniscript

## 목표
- 디스크립터 `wpkh([지문/84h/0h/0h]xpub…/0/*)#체크섬`을 요소별로 읽고 쓴다.
- Core에서 디스크립터를 조회(`listdescriptors`)·검증(`getdescriptorinfo`)·펼치기(`deriveaddresses`)·가져오기(`importdescriptors`)한다.
- miniscript가 해결하는 문제(모든 지출 경로, 최대 witness 크기, 표준 정책 위반)를 설명하고 조건을 정책으로 쓴다.

| 함수 | 결과 |
|---|---|
| `pkh(KEY)` | P2PKH |
| `sh(wpkh(KEY))` | P2SH-P2WPKH |
| `wpkh(KEY)` | P2WPKH |
| `tr(KEY)` | P2TR 단일 키 |
| `wsh(multi(2,K1,K2,K3))` / `wsh(sortedmulti(…))` | P2WSH 멀티시그 (6-2) |
| `tr(KEY,{리프,리프})` | Taproot 스크립트 트리 (6-5) |
| `addr(주소)` · `raw(hex)` | 그대로 |

## 파일
- `descriptor_lab.sh` — 실습 ①~④ (s44-lab1, s44-lab2). regtest 노드와 alice 지갑 필요
- `descriptor_offline.py` — 같은 디스크립터를 `lib`만으로 펼쳐 `deriveaddresses`와 대조 (pkh · sh(wpkh) · wpkh · tr 단일 키)
- `policy_exercises.md` — 실습 ⑤ 정책 쓰기 정답

## 실습 순서
1. `listdescriptors` → 8개(pkh · sh(wpkh) · wpkh · tr × 받는용·잔돈용). 함수·지문·경로(84h/1h/0h, regtest라 coin_type 1h)를 해부도와 대조. `internal: true`가 잔돈용
2. 받는용 wpkh 디스크립터를 `DESC`에 꺼내 `getdescriptorinfo`, `deriveaddresses "$DESC" "[0,4]"` (지갑 없이!) → `getnewaddress`와 순서대로 대조
3. `watch2`(disable_private_keys, blank)에 `importdescriptors` (timestamp 0) → `getbalances`의 `mine.trusted`에 alice의 bech32 코인이 보인다 → 5-4 PSBT의 워치온리 구성
4. xpub 한 글자를 바꾸고 체크섬은 그대로 → `getdescriptorinfo` 오류
5. `policy_exercises.md`

## 실행
```bash
python part2/lesson-17/descriptor_offline.py                 # 테스트 니모닉 예시 (노드 불필요)
bash   part2/lesson-17/descriptor_lab.sh                     # regtest 노드 필요
python part2/lesson-17/descriptor_offline.py "$DESC" 0 4     # Core에서 꺼낸 디스크립터로
```

## 기대 출력
`descriptor_offline.py` 인자 없이 (공개된 테스트 니모닉, 결정적)
```
예시 디스크립터: wpkh([73c5da0a/84h/1h/0h]tpubDC8msFGeGuwnKG9Upg7DM2b4DaRqg3CUZa5g8v2SRQ6K4NSkxUgd7HsL2XVWbVm39yBA4LAxysQAm397zwQSQoQgewGiYZqrA9DsP4zbQ1M/0/*)
0 bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk
1 bcrt1qd7spv5q28348xl4myc8zmh983w5jx32cs707jh
2 bcrt1qxdyjf6h5d6qxap4n2dap97q4j5ps6ua8jkxz0z
3 bcrt1qynpgs6wap6h9uvy7j0xlesew2w82qn039tzepj
4 bcrt1q677973lw0w796gttpy52f296jqaaksz0kadvlr
```
이 디스크립터의 체크섬은 `#evh9fu0w`다(Core 디스크립터 체크섬 알고리즘으로 계산). Core에서 `getdescriptorinfo`로 같은 값이 나오는지 확인해 볼 수 있다.

`descriptor_lab.sh` — alice 지갑의 키는 실행마다 다르다. 형태 예시(값은 위 테스트 니모닉 것을 빌려 씀, 실행마다 다름):
```
DESC=wpkh([73c5da0a/84h/1h/0h]tpubDC8msFGeGuwnKG9Upg7DM2b4DaRqg3CUZa5g8v2SRQ6K4NSkxUgd7HsL2XVWbVm39yBA4LAxysQAm397zwQSQoQgewGiYZqrA9DsP4zbQ1M/0/*)#evh9fu0w (실행마다 다름)
{
  "descriptor": "wpkh([73c5da0a/84h/1h/0h]tpubDC8m…/0/*)#evh9fu0w",
  "checksum": "evh9fu0w",
  "isrange": true,
  "issolvable": true,
  "hasprivatekeys": false
}
[
  "bcrt1q6rz28mcfaxtmd6v789l9rrlrusdprr9pz3cppk",
  …
]
```
- `deriveaddresses`와 `descriptor_offline.py`의 주소 다섯 개가 같아야 한다.
- 3단계 `getbalances`의 `mine.trusted`가 alice의 bech32 받는 주소 잔액과 같아야 한다.
- 4단계는 `Provided checksum 'evh9fu0w' does not match computed checksum '…'` 형태의 오류가 나야 한다.

## 퀴즈
`quiz/lesson-17.md`
