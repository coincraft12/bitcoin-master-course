# 비트코인 마스터 코스 · 실습 저장소

[coincraft.io](https://coincraft.io) 비트코인 마스터 코스(5부 14강 60차시)의 실습 저장소입니다. 원리를 직접 구현하고, 그 결과를 검증용 테스트 벡터와 내 노드로 대조합니다.

> `lib/`는 교육용 구현입니다. 실제 자금에 쓰지 마세요.

## 구조

```
bitcoin-master-course/
  env/        bitcoin.conf, setup_regtest.sh, reset_regtest.sh
  lib/        직접 구현하는 라이브러리 (강을 거치며 자람)
  part1/ ~ part5/lesson-XX/   차시별 코드 + README(기대 출력)
  data/       예제 hex, 테스트 벡터 (출처: data/SOURCES.md)
  quiz/       차시별 퀴즈
  tests/      lib 자동 테스트
```

`lib/`는 강을 따라 자랍니다.

| 강 | 추가되는 모듈 |
|---|---|
| 2강 | `rpc.py` |
| 3강 | `hashes.py`, `ripemd160.py`, `ec.py`, `keys.py`, `base58.py`, `segwit_addr.py` |
| 4강 | `bip39.py`, `bip32.py` |
| 5강 | `tx.py` |
| 6강 | `script.py`, `taproot.py` |
| 7강 | `ecdsa.py`, `schnorr.py`, `sighash.py` |
| 10~11강 | `block.py` |

함수 목록은 [`lib/API.md`](lib/API.md)에 있습니다.

## 준비

1. **Bitcoin Core 31.1** 설치와 배포본 검증: [`env/README.md`](env/README.md) (2-1)
2. **Python 3.10 이상**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   # 7강 교차 확인(선택): pip install coincurve
   ```
3. **표준 실습 환경** (2-2): regtest 노드 + 지갑 miner·alice·bob
   ```bash
   cp env/bitcoin.conf ~/.bitcoin/bitcoin.conf     # macOS: ~/Library/Application Support/Bitcoin/
   ./env/setup_regtest.sh
   ```
   실습이 꼬이면 `./env/reset_regtest.sh` 후 다시 `setup_regtest.sh`.
4. 쉘 실습 일부는 `jq`를 씁니다.

모든 스크립트는 **저장소 최상위에서** 실행합니다.

```bash
python3 part1/lesson-08/recent_blocks.py
```

## lib 테스트

```bash
python3 -m pytest -q tests
```

BIP39·BIP32·BIP173/350·BIP340·BIP341·BIP143 공식 벡터와 Bitcoin Core 테스트 데이터로 검증합니다.

## 미니 과제

| 과제 | 위치 |
|---|---|
| 1부 · 내 노드로 만든 탐색기 리포트 | `part1/lesson-08/assignment/` |
| 2부 · 나의 복구 키트 | `part2/lesson-18/assignment/` |
| 5강 · 세 유형 송금 비교표 | `part3/lesson-22/assignment/` |
| 6강 · 상속형 Taproot 지갑 설계 | `part3/lesson-27/assignment/` |
| 3부 · 지갑 없이 Taproot 송금 | `part3/lesson-31/assignment/` |
| 8강 · RBF vs CPFP 보고서 | `part4/lesson-36/assignment/` |
| 9강 · 내 노드 네트워크 보고서 | `part4/lesson-39/assignment/` |
| 10강 · 재조직 보고서 | `part4/lesson-43/assignment/` |
| 4부 · 내 노드로 만든 네트워크 리포트 | `part4/lesson-48/assignment/` |
| 12강 · 우리 집 상속·복구 설계 | `part5/lesson-52/assignment/` |
| 13강 · L2 비교표 | `part5/lesson-56/assignment/` |
| 최종 프로젝트 · signet에서 Taproot 볼트 지갑 | `part5/lesson-60/final_project/` |

각 과제 폴더의 `exercise_*.py`가 시작 파일이고, `solution/`에 풀이가 있습니다.

## 차시 목록

### 1부 기초 · `part1/`

| 차시 | 폴더 | 제목 |
|---|---|---|
| 1-1 | [`lesson-01`](part1/lesson-01/) | 디지털 화폐의 난제: 이중지불과 신원 없는 합의 |
| 1-2 | [`lesson-02`](part1/lesson-02/) | 백서 다시 읽기: 12개 절과 지금의 차이 |
| 1-3 | [`lesson-03`](part1/lesson-03/) | 트랜잭션 하나의 일생: 송금 버튼부터 확인까지 |
| 1-4 | [`lesson-04`](part1/lesson-04/) | UTXO 모델: 잔액이 아니라 코인이 있다 |
| 2-1 | [`lesson-05`](part1/lesson-05/) | Bitcoin Core 구조: 구성 프로그램, 데이터 디렉터리, 배포본 검증, 표준 설정 |
| 2-2 | [`lesson-06`](part1/lesson-06/) | 네트워크 모드: mainnet·testnet4·signet·regtest와 과정 표준 환경 |
| 2-3 | [`lesson-07`](part1/lesson-07/) | bitcoin-cli와 RPC: JSON-RPC 구조, 조회 연쇄, RPC 보안 |
| 2-4 | [`lesson-08`](part1/lesson-08/) | Python으로 노드 제어: RPC 래퍼, Decimal, 1부 미니 과제 |

### 2부 키와 지갑 · `part2/`

| 차시 | 폴더 | 제목 |
|---|---|---|
| 3-1 | [`lesson-09`](part2/lesson-09/) | 공개키 암호와 secp256k1: 일방향 함수, 타원곡선, 키 생성, lib/ec.py |
| 3-2 | [`lesson-10`](part2/lesson-10/) | 공개키 형식: 비압축·압축·x-only와 y 복원 |
| 3-3 | [`lesson-11`](part2/lesson-11/) | 레거시 주소: HASH160, Base58Check, P2SH, WIF |
| 3-4 | [`lesson-12`](part2/lesson-12/) | SegWit 주소: bech32, P2WPKH, P2WSH, 중첩 SegWit |
| 3-5 | [`lesson-13`](part2/lesson-13/) | Taproot 주소: bech32m, P2TR, 유형별 크기 비교 |
| 4-1 | [`lesson-14`](part2/lesson-14/) | 시드와 니모닉: BIP39, 체크섬, PBKDF2, 패스프레이즈 |
| 4-2 | [`lesson-15`](part2/lesson-15/) | HD 키 파생: BIP32 마스터 키, 일반·강화 파생, xpub 위험 |
| 4-3 | [`lesson-16`](part2/lesson-16/) | 파생 경로 표준: purpose, 갭 리밋, 잔액 0 진단 |
| 4-4 | [`lesson-17`](part2/lesson-17/) | 출력 디스크립터와 miniscript |
| 4-5 | [`lesson-18`](part2/lesson-18/) | 지갑 백업과 복구, 2부 미니 과제 |

### 3부 트랜잭션과 스크립트 · `part3/`

| 차시 | 폴더 | 제목 |
|---|---|---|
| 5-1 | [`lesson-19`](part3/lesson-19/) | 입력과 출력: outpoint, 금액, 수수료, 코인베이스 |
| 5-2 | [`lesson-20`](part3/lesson-20/) | 직렬화와 witness: CompactSize, 가변성, txid·wtxid, weight·vsize, 파서 |
| 5-3 | [`lesson-21`](part3/lesson-21/) | 잔돈과 코인 선택: 잔돈 누락, 더스트, 코인 선택 알고리즘 |
| 5-4 | [`lesson-22`](part3/lesson-22/) | PSBT: 역할 분리, 워치온리·서명 지갑 실습, 5강 미니 과제 |
| 6-1 | [`lesson-23`](part3/lesson-23/) | Script 언어: 스택 머신, opcode, P2PKH 추적, 간이 실행기 |
| 6-2 | [`lesson-24`](part3/lesson-24/) | 멀티시그: CHECKMULTISIG, P2SH·P2WSH, 2-of-3 PSBT 실습 |
| 6-3 | [`lesson-25`](part3/lesson-25/) | 타임락: nLockTime, nSequence, CLTV, CSV 실습 |
| 6-4 | [`lesson-26`](part3/lesson-26/) | Taproot 키 경로: 키 조정, 출력키 계산 |
| 6-5 | [`lesson-27`](part3/lesson-27/) | Taproot 스크립트 경로: 트리, 컨트롤 블록, NUMS, 6강 미니 과제 |
| 7-1 | [`lesson-28`](part3/lesson-28/) | ECDSA: 서명·검증, low-S, DER, 구현 |
| 7-2 | [`lesson-29`](part3/lesson-29/) | 논스 재사용 공격: 개인키 복원, 사고 연표, RFC6979·anti-exfil |
| 7-3 | [`lesson-30`](part3/lesson-30/) | Schnorr 서명: BIP340 설계, 구현, 테스트 벡터 |
| 7-4 | [`lesson-31`](part3/lesson-31/) | Sighash와 MuSig2, 3부 미니 과제 |

### 4부 네트워크와 합의 · `part4/`

| 차시 | 폴더 | 제목 |
|---|---|---|
| 8-1 | [`lesson-32`](part4/lesson-32/) | 수수료 시장: 블록 공간 경매, 추정, 보안 예산 |
| 8-2 | [`lesson-33`](part4/lesson-33/) | 멤풀 정책: 합의 vs 정책, 정책 항목, 더스트 실습 |
| 8-3 | [`lesson-34`](part4/lesson-34/) | RBF: 대체 규칙, full RBF, 0-확인 위험 |
| 8-4 | [`lesson-35`](part4/lesson-35/) | CPFP와 패키지 릴레이 |
| 8-5 | [`lesson-36`](part4/lesson-36/) | TRUC와 클러스터 멤풀, 8강 미니 과제 |
| 9-1 | [`lesson-37`](part4/lesson-37/) | 노드 발견과 연결, 일식 공격 |
| 9-2 | [`lesson-38`](part4/lesson-38/) | 전파 프로토콜, 컴팩트 블록, 2노드 실습 |
| 9-3 | [`lesson-39`](part4/lesson-39/) | 경량 클라이언트와 네트워크 프라이버시, 9강 미니 과제 |
| 10-1 | [`lesson-40`](part4/lesson-40/) | 블록 헤더 |
| 10-2 | [`lesson-41`](part4/lesson-41/) | 머클 트리 |
| 10-3 | [`lesson-42`](part4/lesson-42/) | 체인 선택과 재조직 |
| 10-4 | [`lesson-43`](part4/lesson-43/) | 초기 블록 다운로드, 10강 미니 과제 |
| 11-1 | [`lesson-44`](part4/lesson-44/) | 작업증명과 난이도 조정 |
| 11-2 | [`lesson-45`](part4/lesson-45/) | 발행 스케줄과 반감기 |
| 11-3 | [`lesson-46`](part4/lesson-46/) | 채굴 풀과 Stratum V2 |
| 11-4 | [`lesson-47`](part4/lesson-47/) | 합의 규칙과 포크 |
| 11-5 | [`lesson-48`](part4/lesson-48/) | 소프트포크 활성화, 4부 미니 과제 |

### 5부 실전과 확장 · `part5/`

| 차시 | 폴더 | 제목 |
|---|---|---|
| 12-1 | [`lesson-49`](part5/lesson-49/) | 위협 모델과 사례, 주소 중독 실습 |
| 12-2 | [`lesson-50`](part5/lesson-50/) | 하드웨어 지갑과 에어갭, 오프라인 서명 실습 |
| 12-3 | [`lesson-51`](part5/lesson-51/) | 기관 커스터디와 볼트 설계 |
| 12-4 | [`lesson-52`](part5/lesson-52/) | 상속과 비상 복구, 12강 미니 과제 |
| 13-1 | [`lesson-53`](part5/lesson-53/) | 라이트닝 네트워크 원리 |
| 13-2 | [`lesson-54`](part5/lesson-54/) | 라이트닝 실무와 LND 실습 |
| 13-3 | [`lesson-55`](part5/lesson-55/) | 사이드체인과 페더레이션, 2026 Liquid 사고 |
| 13-4 | [`lesson-56`](part5/lesson-56/) | BitVM과 비트코인 롤업, 13강 미니 과제 |
| 14-1 | [`lesson-57`](part5/lesson-57/) | 블록 공간 논쟁과 BIP-110 |
| 14-2 | [`lesson-58`](part5/lesson-58/) | 다음 소프트포크 후보와 BIP54 |
| 14-3 | [`lesson-59`](part5/lesson-59/) | 프라이버시와 양자내성 |
| 14-4 | [`lesson-60`](part5/lesson-60/) | 제도권 편입, 과정 마무리와 최종 프로젝트 |

## 슬라이드와 다른 곳

슬라이드 코드를 그대로 두면 실행이 막히는 몇 곳은 저장소에서 보완했습니다. 목록은 [`ERRATA.md`](ERRATA.md)에 있습니다.
