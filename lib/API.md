# lib 공개 API (2부: 3·4강에서 만든 기초 모듈)

모든 모듈은 표준 라이브러리만 쓴다. 저장소 최상위를 `sys.path`에 넣은 뒤 `from lib.xxx import …`로 가져온다.
점은 `(x, y)` 정수 튜플, 무한원점은 `None`. 개인키는 정수, 바이트열은 `bytes`.

## lib/hashes.py (3-3)
```
sha256(b: bytes) -> bytes
dsha256(b: bytes) -> bytes                 # SHA256 두 번
hash256 = dsha256                          # 같은 함수의 다른 이름
hash160(b: bytes) -> bytes                 # RIPEMD160(SHA256(b))
tagged_hash(tag: str, msg: bytes) -> bytes # BIP340 SHA256(SHA256(tag)‖SHA256(tag)‖msg)
```

## lib/ripemd160.py (3-3, Bitcoin Core 테스트 프레임워크 원본)
```
ripemd160(data: bytes) -> bytes
```

## lib/ec.py (3-1) — secp256k1, 슬라이드 그대로
```
FIELD_P: int   N: int   G: tuple
is_on_curve(P) -> bool
point_add(P, Q) -> point | None
point_mul(P, k: int) -> point | None       # 점이 먼저, 스칼라가 나중
```

## lib/base58.py (3-3)
```
ALPHABET: str
b58encode(b: bytes) -> str
b58decode(s: str) -> bytes                 # 알파벳 밖 문자는 ValueError
b58check_encode(payload: bytes) -> str
b58check_decode(s: str) -> bytes           # 체크섬 불일치는 ValueError("체크섬 불일치")
```

## lib/keys.py (3-1 ~ 3-5)
```
new_private_key() -> int                                   # secrets, 1..N-1
public_key(d: int) -> point                                # point_mul(G, d)
ser_uncompressed(Q) -> bytes                               # 65B 04‖x‖y
ser_compressed(Q) -> bytes                                 # 33B 02/03‖x
ser_xonly(Q) -> bytes                                      # 32B x
parse_pubkey(b: bytes) -> point                            # 65B/33B, y 복원, 곡선 위 검사 (ValueError)
parse_xonly(b: bytes) -> point                             # 32B → 짝수 y 점
p2pkh_address(pubkey: bytes, version: int = 0x00) -> str   # regtest 0x6f
p2sh_address(redeem_script: bytes, version: int = 0x05) -> str   # regtest 0xc4
wif(d: int, compressed: bool = True, version: int = 0x80) -> str  # regtest 0xef
parse_wif(s: str) -> (d: int, compressed: bool, version: int)
p2wpkh_address(pubkey_compressed: bytes, hrp: str = "bc") -> str  # regtest "bcrt"
p2wsh_address(witness_script: bytes, hrp: str = "bc") -> str
p2sh_p2wpkh_address(pubkey_compressed: bytes, version: int = 0x05) -> str
p2tr_address(output_xonly: bytes, hrp: str = "bc") -> str  # 이미 조정된 출력키 32B → bech32m v1
address_to_script_pubkey(addr: str) -> bytes               # P2PKH/P2SH/모든 witness 주소 → scriptPubKey
P2PKH_VERSIONS = (0x00, 0x6f)   P2SH_VERSIONS = (0x05, 0xc4)   HRPS = ("bc", "tb", "bcrt")
```

## lib/segwit_addr.py (3-4, 3-5) — BIP173/BIP350 참조 구현 그대로
```
encode(hrp: str, witver: int, witprog: bytes|list) -> str | None
decode(hrp: str, addr: str) -> (witver, list[int]) | (None, None)   # 프로그램은 int 리스트 → bytes(prog)
bech32_encode(hrp, data: list[int], spec: Encoding) -> str
bech32_decode(bech: str) -> (hrp, data, spec) | (None, None, None)
convertbits(data, frombits, tobits, pad=True) -> list | None
Encoding.BECH32 / Encoding.BECH32M   CHARSET   BECH32M_CONST
```

## lib/bip39.py (4-1)
```
WORDS: list[str]                                           # data/bip39_english.txt
nfkd(s: str) -> str
entropy_to_mnemonic(ent: bytes) -> str
mnemonic_to_entropy(mnemonic: str) -> bytes                # 체크섬 검사 없음
is_valid(mnemonic: str) -> bool
mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes   # 64B, PBKDF2-HMAC-SHA512 2048회
new_mnemonic(words: int = 12) -> str
```

## lib/bip32.py (4-2)
```
HARD = 0x80000000
VERSIONS = {"xprv", "xpub", "tprv", "tpub": 4바이트}
hmac512(key: bytes, data: bytes) -> bytes
master(seed: bytes) -> (k: int, c: bytes)
ckd_priv(k: int, c: bytes, i: int) -> (k, c)
ckd_pub(K, c: bytes, i: int) -> (K, c)                     # 강화 번호면 ValueError
parse_path(path: str) -> list[int]                         # "m/84h/1'/0H/0/5", 상대 경로 "0/5"도 가능
derive_priv(seed: bytes, path: str) -> (k, c)
derive_pub(K, c: bytes, path: str) -> (K, c)               # 일반 파생 상대 경로만
fingerprint(K) -> bytes                                    # HASH160(압축 공개키)[:4]
derive_ext(seed: bytes, path: str) -> (k, c, depth, parent_fp: bytes, child: int)
serialize(key, c, depth=0, parent_fp=b"\0"*4, child=0, testnet=False) -> str   # int → xprv/tprv, 점 → xpub/tpub
derive_xprv(seed: bytes, path: str, testnet: bool = False) -> str
derive_xpub(seed: bytes, path: str, testnet: bool = False) -> str
parse_extended(s: str) -> dict   # version, depth, parent_fp, child, chain_code, key(int|점), private, testnet. 무효면 ValueError
neuter(s: str) -> str                                      # xprv/tprv → xpub/tpub
```

## lib/taproot.py (6-4 최소판 · 6강에서 확장)
6-4 슬라이드 코드 그대로. 4-3 BIP86 주소와 2부 과제에서 미리 쓴다. 6-5(tapleaf_hash 등)와 7-3(lift_x의 x ≥ FIELD_P 검사)이 이어서 추가한다.
```
tagged_hash(tag: str, msg: bytes) -> bytes
lift_x(x: int) -> point                                    # 짝수 y, 곡선 밖이면 ValueError
output_key(internal_xonly: bytes, merkle_root: bytes = b"") -> bytes   # 32B 출력키
```

## lib/rpc.py (2-4, 이미 있던 파일)
```
RPC(network="regtest", wallet=None, datadir=…)   btc_to_sat, sat_to_btc
```

## 아직 없는 모듈 (다른 강에서 작성)
~~tx.py(5강), script.py(6-1), ecdsa.py·schnorr.py·sighash.py(7강), block.py(10·11강).~~ → 모두 작성됨. 3부 모듈은 아래 "3부 (5~7강)" 절, block.py는 아래 절.

## lib/block.py (10·11강) — 블록 헤더, 머클, 작업증명, 보조금
슬라이드 코드(s101-lab, s102-lab, s111-lab1, s112-lab) 그대로 + 저장소가 보탠 함수. `lib.hashes.dsha256`만 쓴다.
헤더 안 해시와 블록 해시는 표시할 때 뒤집는다(16진수 문자열은 표시 순서). 정수 필드는 리틀 엔디안.
```
# 슬라이드 그대로
parse_header(h: bytes) -> dict             # 80B → version, prev, merkle_root, time, bits, nonce, hash (80B 아니면 AssertionError)
bits_to_target(bits: int) -> int           # 가수 × 256^(지수−3). 지수 < 3은 다루지 않는다(ERRATA s101-lab)
check_pow(h: bytes) -> bool                # int(블록 해시) ≤ 타깃
merkle_root(txids: list[str]) -> str       # 표시 순서 txid 목록 → 표시 순서 루트. 홀수면 마지막 복제, 빈 목록 ValueError
mine(prefix76: bytes, zero_bits: int, max_tries: int = 2**32) -> (nonce, hash_hex, 초) | None
POW_LIMIT = 0x00000000FFFF << 208          TWO_WEEKS = 2016 * 600
retarget(old_target: int, actual_timespan: int) -> int    # 1/4~4배로 자른 비율, POW_LIMIT 상한
COIN = 100_000_000
subsidy(height: int, interval: int = 210_000) -> int      # sat. 반감 64번 이상이면 0. regtest는 interval=150
total_supply(interval: int = 210_000) -> int              # 2_099_999_997_690_000 sat

# 저장소가 보탠 것
serialize_header(fields: dict) -> bytes    # parse_header의 역 (version, prev, merkle_root, time, bits, nonce)
header_hash(h: bytes) -> str
target_to_bits(target: int) -> int         # Core GetCompact (부호 비트면 지수 +1)
DIFF1_TARGET                               # bits_to_target(0x1d00ffff)
difficulty(bits: int) -> float             # 난이도 1 타깃 ÷ 타깃 (getdifficulty와 같은 정의)
block_work(bits: int) -> int               # 2^256 // (타깃+1), chainwork 한 블록분
next_bits(old_bits, first_block_time, last_block_time) -> int   # retarget → target_to_bits (Core pow_tests 벡터와 일치)
merkle_proof(txids, index) -> list[str]    # 형제 해시(내부 순서 16진수), 아래층부터
root_from_proof(txid, index, proof) -> str
verify_merkle_proof(txid, index, proof, root) -> bool
parse_merkleblock(proof_hex: str) -> dict  # gettxoutproof 결과 → header(80B), n_tx, hashes(내부 순서 bytes), bits(list[bool])
extract_matches(pmt: dict) -> (root, [(위치, txid), ...])   # Core CPartialMerkleTree 순회, 형식 오류·중복 오른쪽은 ValueError
build_merkleblock(header: bytes, txids, match: set) -> str  # gettxoutproof와 같은 형식의 hex
VERSIONBITS_TOP_BITS = 0x20000000   VERSIONBITS_TOP_MASK = 0xE0000000
signals_bit(version: int, bit: int) -> bool                 # BIP9 형식이고 그 비트가 켜졌는지
```
테스트: `tests/test_block.py` (제네시스 4종, testnet3 실제 헤더 10개, 블록 100,000 머클, Core 난이도 조정 벡터 4건, 보조금·총 발행량, regtest 150 반감).

# 3부 (5~7강) — 트랜잭션, Script, Taproot 트리, 서명, 서명 해시

점은 `(x, y)` 정수 튜플. 트랜잭션은 `parse_tx`가 돌려주는 dict 그대로 주고받는다. 금액은 언제나 sat 정수.

## lib/tx.py (5-2 · 3부 미니 과제)
```
# 슬라이드 그대로 (s52-code1~3)
dsha256(b: bytes) -> bytes
read_varint(b: bytes, i: int) -> (값, 다음 위치)
parse_tx(hexstr: str) -> dict            # 남는 바이트가 있으면 AssertionError
    {"version", "segwit", "vin", "vout", "locktime", "txid", "wtxid", "size", "weight", "vsize"}
    vin[i]  = {"txid"(표시 순서 hex), "vout", "scriptSig"(hex), "sequence"} + SegWit이면 "witness": [hex, …]
    vout[i] = {"value_sat", "scriptPubKey"(hex)}
    size = 전체 바이트(Core decoderawtransaction의 size) · weight = base×3 + size · vsize = (weight+3)//4
# 3부 미니 과제 03에서 추가 (s7-assign)
write_varint(n: int) -> bytes            # CompactSize 쓰기
serialize_tx(tx: dict, include_witness: bool = True) -> bytes
    # witness 항목이 하나라도 있으면 SegWit 형식. parse_tx(serialize_tx(t).hex())로 txid·vsize 재계산
```

## lib/script.py (6-1) — 간이 실행기, 슬라이드 그대로
```
OPS: dict[int, str]                      # 실행기가 다루는 opcode 12개
parse_script(b: bytes) -> list           # push 데이터는 bytes, opcode는 이름 문자열, 표에 없으면 "OP_UNKNOWN_0x.."
is_true(v: bytes) -> bool                # 음수 0 규칙 생략
run(script_sig, script_pubkey, checksig=lambda sig, pub: True, trace=True) -> bool
    # 두 스크립트를 따로 파싱해 차례로 실행(스택만 이어받음). OPS 밖 opcode 실행은 NotImplementedError
    # checksig(sig_with_hashtype_byte, pubkey) -> bool 자리에 7강 검증을 끼운다 (part3/lesson-31/checksig_p2pkh.py)
```

## lib/taproot.py (6-4 · 6-5 · 7-3) — 위 6-4 최소판 세 함수는 시그니처 그대로
```
tagged_hash(tag: str, msg: bytes) -> bytes
lift_x(x: int) -> point                  # 짝수 y. x ≥ FIELD_P(7-3에서 추가) 또는 곡선 밖이면 ValueError
output_key(internal_xonly: bytes, merkle_root: bytes = b"") -> bytes
# 6-5 s65-code 그대로
ser_compact(n) -> bytes                  # 0xfd 미만 1B, 그 이상 0xfd+2B (스크립트 길이용)
tapleaf_hash(script: bytes, leaf_version=0xc0) -> bytes
tapbranch_hash(a: bytes, b: bytes) -> bytes             # 사전순 정렬 후 TapBranch
verify_script_path(output_xonly, script, control) -> bool   # 패리티 검사는 단순화로 생략
# 6-5 트리·컨트롤 블록·NUMS를 코드로
NUMS_H: bytes                            # 50929b74…803ac0 (BIP341 NUMS H의 x)
nums_h() -> bytes                        # lift_x(SHA256(G 비압축)) 직접 계산
taproot_tree(tree) -> ([(leaf_version, script, path_bytes)], merkle_root)
    # tree: None | 잎 {"script": bytes|hex, "leafVersion": int} 또는 (script, leaf_version) | 가지 [왼쪽, 오른쪽]
    # (BIP341 wallet-test-vectors scriptTree와 같은 모양). 잎 순서 = 왼쪽부터. 트리 없음이면 ([], b"")
tweak_pubkey(internal_xonly: bytes, merkle_root: bytes = b"") -> (parity: int, output_xonly: bytes)
control_block(internal_xonly, leaf_version: int, path: bytes, merkle_root: bytes) -> bytes   # (버전|패리티) ‖ 내부키 ‖ 경로
p2tr_script_pubkey(output_xonly: bytes) -> bytes        # 0x51 0x20 ‖ Q
```

## lib/ecdsa.py (7-1 · 7-2)
```
# 슬라이드 그대로 (s71-code1·2)
sign(d: int, z: int, k: int | None = None) -> (r, s)   # k 없으면 secrets 난수. low-S로 정규화
verify(Q, z: int, r: int, s: int) -> bool              # high-S도 통과(수학적으로 유효)
der(r: int, s: int) -> bytes                           # sighash 바이트 없는 DER 본문
# 저장소가 보탠 것
parse_der(sig: bytes) -> (r, s)                        # sighash 바이트를 뗀 DER. 형식 오류 ValueError
rfc6979_nonce(d: int, z: int) -> int                   # RFC 6979 3.2 HMAC-SHA256 (7-2 "lib ecdsa.py에 RFC6979 추가")
sign_rfc6979(d: int, z: int) -> (r, s)                 # 결정적 서명. BIP143 예제 서명·libsecp256k1과 바이트 일치
```
z는 서명 해시(32B)를 빅 엔디안 정수로 읽은 값.

## lib/schnorr.py (7-3) — BIP340, 슬라이드 그대로
```
b32(x: int) -> bytes   to_int(b: bytes) -> int   even_y(P) -> bool   xor(a: bytes, b: bytes) -> bytes
sign(msg: bytes, seckey: bytes, aux_rand: bytes) -> bytes      # 64B. seckey 32B (범위 밖이면 AssertionError)
verify(msg: bytes, pubkey: bytes, sig: bytes) -> bool          # pubkey x-only 32B
pubkey_gen(seckey: bytes) -> bytes                             # 저장소가 보탠 것: x-only 32B
```

## lib/sighash.py (7-4)
```
# 슬라이드 그대로 (s74-code1·2)
sha(b) -> bytes                          # 단일 SHA256
outpoint(i: dict) -> bytes               # 뒤집은 txid ‖ vout 4B LE
ser_out(o: dict) -> bytes                # 금액 8B ‖ 길이 ‖ scriptPubKey
taproot_sighash(tx, prevouts, idx, hash_type=0x00) -> bytes    # BIP341 키 경로·annex 없음. prevouts = [(sat, spk bytes)] 모든 입력
# s74-amount의 나머지 두 방식
SIGHASH_ALL = 0x01  SIGHASH_NONE = 0x02  SIGHASH_SINGLE = 0x03  SIGHASH_ANYONECANPAY = 0x80
p2wpkh_script_code(pubkey_hash: bytes) -> bytes                # 76a914{20B}88ac
bip143_sighash(tx, idx, script_code: bytes, amount: int, hash_type=0x01) -> bytes   # SegWit v0
legacy_sighash(tx, idx, script_code: bytes, hash_type=0x01) -> bytes                # Core SignatureHash(BASE)
    # OP_CODESEPARATOR 제거, 범위 밖 입력·SINGLE 짝 없음 → 1 (Core와 같은 옛 동작)
```
반환값은 모두 32바이트 내부 순서. Core·문서가 찍는 레거시 sighash는 뒤집은 hex다.

테스트: `tests/test_tx.py`, `test_script.py`, `test_taproot.py`(+ `test_taproot_min.py`), `test_ecdsa.py`, `test_schnorr.py`,
`test_sighash.py`, `test_part3_assignment.py` — BIP340 19개, BIP341 scriptPubKey 7개·키 경로 7개, BIP143 예제 13개,
Core sighash.json 500개, RFC6979(BIP143 서명 12개 재현·libsecp256k1 교차), T-02 블록 170 서명.
