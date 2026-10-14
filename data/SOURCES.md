# data/ 출처

공식 데이터는 아래 URL에서 받은 원본 그대로다. 손으로 옮겨 적지 않았다.

## 2부 (3·4강) — 받은 날짜 2026-10-14

| 파일 | 출처 | 처리 |
|---|---|---|
| `bip39_english.txt` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt | 원본 그대로 (sha256 2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda) |
| `bip39_vectors.json` | https://raw.githubusercontent.com/trezor/python-mnemonic/master/vectors.json | 원본 그대로. 테스트는 `english` 항목 전체 사용 (패스프레이즈 "TREZOR") |
| `bip32_vectors.json` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0032.mediawiki | "Test Vectors" 절의 벡터 1~4(시드·경로·xpub·xprv)와 벡터 5(무효 확장 키 16개와 사유)를 정규식으로 추출 (`<sub>H</sub>` → `h`) |
| `bip340_test_vectors.csv` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0340/test-vectors.csv | 원본 그대로 (7강용) |
| `bech32_vectors.json` | https://raw.githubusercontent.com/sipa/bech32/master/ref/python/tests.py (BIP173·BIP350 참조 테스트) | 리스트 리터럴(VALID_BECH32, VALID_BECH32M, INVALID_BECH32, INVALID_BECH32M, VALID_ADDRESS, INVALID_ADDRESS, INVALID_ADDRESS_ENC)을 실행 없이 구문 분석으로 추출 |
| `base58_encode_decode.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/master/src/test/data/base58_encode_decode.json | 원본 그대로 |
| `key_io_valid.json`, `key_io_invalid.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/master/src/test/data/key_io_valid.json · key_io_invalid.json | 원본 그대로. WIF(isPrivkey)와 주소→scriptPubKey 대조에 사용 |
| `bip_derivation_vectors.json` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0084.mediawiki · bip-0086.mediawiki · bip-0049.mediawiki | 각 문서 "Test vectors"의 니모닉·경로·공개키·출력키·주소를 정규식으로 추출 (BIP49는 문서의 testnet 벡터) |
| `lesson03_examples.json` | 3-3 s33-vectors, 3-4 s34-q 슬라이드 값 (개인키 1) | lib로 다시 계산해 슬라이드 값과 일치를 확인한 뒤 regtest 버전 값 등을 덧붙임 |
| `T-03/spend_*.hex` | 3-5 실습 `part2/lesson-13/measure_sizes.sh`가 수강생 노드에서 생성 | 저장소에는 없음 (실행마다 다름) |

lib에 그대로 넣은 참조 구현
- `lib/segwit_addr.py` ← https://raw.githubusercontent.com/sipa/bech32/master/ref/python/segwit_addr.py (MIT, Pieter Wuille). 모듈 docstring만 바꿈
- `lib/ripemd160.py` ← https://raw.githubusercontent.com/bitcoin/bitcoin/master/test/functional/test_framework/crypto/ripemd160.py (MIT, Pieter Wuille). 모듈 docstring만 바꿈

## 4부 (8~11강) — 받은 날짜 2026-10-14

| 파일 | 출처 | 처리 |
|---|---|---|
| `genesis_blocks.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/v31.1/src/kernel/chainparams.cpp | main·testnet3·signet·regtest의 `CreateGenesisBlock` 인자(time, nonce, bits, version)와 pszTimestamp·출력 공개키로 헤더 80바이트와 코인베이스를 조립하고, dsha256이 각 `assert(hashGenesisBlock == …)`, 코인베이스 txid가 `assert(hashMerkleRoot == …)`와 같음을 확인한 뒤 저장 |
| `block100000.json` | https://raw.githubusercontent.com/btcsuite/btcd/master/btcutil/block_test.go | `Block100000`의 헤더 필드(PrevBlock, MerkleRoot, Timestamp, Bits, Nonce)와 `wantTxHashes` txid 4개를 추출. 조립한 헤더의 해시가 `wantHashStr`(000000000003ba27…)와 같고, txid 4개의 머클 루트가 헤더의 MerkleRoot(f3e94742…)와 같음을 확인 |
| `pow_retarget_vectors.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/v31.1/src/test/pow_tests.cpp | `get_next_work`, `get_next_work_pow_limit`, `get_next_work_lower_limit_actual`, `get_next_work_upper_limit_actual`의 시각·높이·bits·기대 bits를 정규식으로 추출 |
| `blockfilters.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/master/src/test/data/blockfilters.json | 원본 그대로 (BIP158 basic 필터, testnet3 블록 10개). 헤더 해시·필터 헤더 사슬 검증과 9-3 크기 비교에 사용 |
| `coinbase_tags.json` | https://raw.githubusercontent.com/bitcoin-data/mining-pools/generated/pools.json | 원본 그대로 (`coinbase_tags`: 태그 → 풀, `payout_addresses`: 지급 주소 → 풀). 11-3 슬라이드의 "강사 제공 data/coinbase_tags.json" 자리에 쓴다. 블록 데이터가 아니라 태그 사전이므로 점유율은 메인넷 노드나 탐색기로 집계한다 |

그 밖의 4부 수치 출처
- regtest 반감 주기 150, testdummy(bit 28·구간 144·임계치 108), Taproot 배포 파라미터, buried 높이: 위 v31.1 `chainparams.cpp`
- 보조금 함수(64 이상 시프트 0): https://raw.githubusercontent.com/bitcoin/bitcoin/v31.1/src/validation.cpp `GetBlockSubsidy`
- 난이도 조정·4배 제한: https://raw.githubusercontent.com/bitcoin/bitcoin/v31.1/src/pow.cpp `CalculateNextWorkRequired`
- 이중지불 확률 표: 비트코인 백서 11절 계산식(`part4/lesson-42/double_spend_prob.py`가 재계산)

## 3부 (5~7강) — 받은 날짜 2026-10-14

| 파일 | 출처 | 처리 |
|---|---|---|
| `T-02.hex` | 메인넷 블록 170의 두 번째 트랜잭션(첫 P2P 송금, txid f4184fc5…). 공식 저장소에 raw hex가 없고 이 환경에서 블록 탐색기 접속이 막혀, PyPI 패키지의 테스트 데이터에서 꺼냈다: `python-bitcoinlib` 0.12.2 `bitcoin/tests/test_core.py`(블록 170 전체 raw)와 `pycoin` 0.92718.20260405 `tests/annotate_test.py`(같은 트랜잭션) — 두 출처가 바이트 단위로 같다 | SHA256d를 뒤집은 값이 슬라이드의 txid `f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16`과 같음을 확인(해시가 맞으면 원본과 같은 바이트). 서명은 블록 9 출력 공개키로 검증된다(`tests/test_sighash.py`) |
| `T-02_prev.hex` | 블록 9 코인베이스(txid 0437cd7f…). `pycoin` 같은 파일 `test_disassemble`의 입력 트랜잭션 | SHA256d가 슬라이드 s51-lab2의 txid `0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9`와 같음을 확인 |
| `bip341_wallet_test_vectors.json` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0341/wallet-test-vectors.json | 원본 그대로 (scriptPubKey 7개, keyPathSpending 입력 7개) |
| `bip143_examples.json` | https://raw.githubusercontent.com/bitcoin/bips/master/bip-0143.mediawiki | "Example" 절에서 sigHash 13개를 정규식으로 추출(실행 없음): 서명 전·후 트랜잭션, sigHash, 서명, 공개키, 개인키(있으면). 입력 번호·scriptCode·금액·hashType은 문서의 preimage hex를 잘라 읽었다 |
| `sighash.json` | https://raw.githubusercontent.com/bitcoin/bitcoin/master/src/test/data/sighash.json | 원본 그대로 (레거시 SignatureHash 500개: raw tx, script, 입력 번호, hashType, 기대 해시) |
| `demo_txs.json` | 저장소 lib으로 만든 결정적 예제 (`data/make_demo_txs.py`) | 공개 테스트 니모닉 키·**가짜 UTXO**로 P2PKH·P2WPKH·P2TR 입력 지출을 하나씩 만들고 서명(ECDSA RFC6979, Schnorr aux_rand 0). 공식 데이터가 아니다. `tests/test_tx.py`가 재생성 결과와 같은지 확인 |
| `T-03/` | 3-5 `part2/lesson-13/measure_sizes.sh`가 수강생 노드에서 생성 (6-1 실행 추적에 `spend_legacy.hex` 사용) | 저장소에는 없음 |
| `bip340_test_vectors.csv` | (2부 표 참고) | 7-3 `tests/test_schnorr.py`, `part3/lesson-30/run_vectors.py`가 19개 전부 사용 |

3부 lesson 폴더에 원본 그대로 넣은 파일
- `part3/lesson-31/musig2/reference.py` ← https://raw.githubusercontent.com/bitcoin/bips/master/bip-0327/reference.py (BIP327 참조 구현, BSD-3-Clause)
- `part3/lesson-31/musig2/vectors/*.json` ← https://raw.githubusercontent.com/bitcoin/bips/master/bip-0327/vectors/ (8개 파일)
- `part3/lesson-27/assignment/solution/descriptors.py` ← https://raw.githubusercontent.com/bitcoin/bitcoin/master/test/functional/test_framework/descriptors.py (MIT, BIP380 디스크립터 체크섬). BIP380 문서의 `raw(deadbeef)#89f8spxm` 예를 재현함을 확인


## 5부 lesson 폴더에 원본 그대로 넣은 파일
- `part5/lesson-60/final_project/solution/descriptors.py` ← https://raw.githubusercontent.com/bitcoin/bitcoin/master/test/functional/test_framework/descriptors.py (MIT, BIP380 디스크립터 체크섬)
- `part5/lesson-60/final_project/solution/tr_vectors.json` ← BIP386·BIP387 문서의 tr() 테스트 벡터 (출처 URL·sha256은 파일 안에 기록)
