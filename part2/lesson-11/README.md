# lesson-11 · 3-3 레거시 주소: HASH160, Base58Check, P2SH, WIF

## 목표
- 공개키 → HASH160 → 버전 바이트 → 체크섬 → Base58로 P2PKH 주소를 직접 계산한다.
- Base58Check 체크섬(4바이트)이 오타를 잡는 원리를 확인한다.
- P2SH(BIP16)의 등장 이유와 WIF 형식(0x80 ‖ 키 ‖ [01])을 설명한다.

## 만드는 코드
- `lib/hashes.py` — `sha256`, `dsha256`(= `hash256`), `hash160`
- `lib/ripemd160.py` — Bitcoin Core 테스트 프레임워크의 순수 Python RIPEMD160 (MIT). OpenSSL 3에서는 `hashlib.new("ripemd160")`이 없는 경우가 많다.
- `lib/base58.py` — `ALPHABET`, `b58encode`, `b58decode`, `b58check_encode`, `b58check_decode`
- `lib/keys.py` — `p2pkh_address(pubkey, version=0x00)`, `p2sh_address(script, version=0x05)`, `wif(d, compressed=True, version=0x80)`, 보충 `parse_wif(s)`

| 유형 | mainnet | testnet·regtest |
|---|---|---|
| P2PKH | 0x00 · 1 | 0x6f · m/n |
| P2SH | 0x05 · 3 | 0xc4 · 2 |
| WIF | 0x80 · K/L(압축), 5(비압축) | 0xef · c(압축), 9(비압축) |

## 실습 순서
1. 해시와 Base58Check 모듈 (s33-code)
2. 개인키 1로 테스트 벡터 검증 (s33-vectors) — 개인키 1은 누구나 아는 키. 이 주소로 절대 송금하지 말 것.
3. Core와 대조: legacy 주소의 pubkey → `p2pkh_address(…, 0x6f)` → 한 글자 바꿔 `b58check_decode`와 `validateaddress`

## 실행
```bash
python part2/lesson-11/address_vectors.py
python part2/lesson-11/check_core_legacy.py 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798 mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
bash   part2/lesson-11/core_legacy.sh          # regtest 노드 필요
```

## 기대 출력
`address_vectors.py` (결정적)
```
OK  p2pkh_address(ser_compressed(G))       1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH
OK  p2pkh_address(ser_uncompressed(G))     1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm
OK  wif(1)                                 KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn

HASH160(압축 공개키): 751e76e8199196d454941c45d1b3a323f1433bd6
비압축 WIF          : 5HpHagT65TZzG1PH3CSu63k8DbpvD8s5ip4nEB3kEsreAnchuDf
regtest P2PKH       : mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
regtest WIF         : cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN87JcbXMTcA
P2SH(P2PK 스크립트) : 34wjDxkCQrUPYwnCRtap5uib6XNcVaud9K

원래 주소 : 1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH
오타 주소 : 1BgGZ9tcN4Zm9KBzDn7KprQz87SZ26SAMH
결과      : 체크섬 불일치
```
`check_core_legacy.py` (위 인자, 결정적. 마지막 줄은 셸 스크립트가 validateaddress에 넘길 오타 주소)
```
내 계산 : mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
Core    : mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
일치    : True
오타 mrCDrCybB6J1vRfbw25hemdJz73FwDBC8r: 체크섬 불일치
mrCDrCybB6J1vRfbw25hemdJz73FwDBC8r
```
`core_legacy.sh` — 주소는 실행마다 다르고, `일치 : True`, `체크섬 불일치`, 그리고 Core도 거부해야 한다.
```
Core validateaddress(오타):
{ "isvalid": false, "error": "Invalid checksum or length of Base58 address (P2PKH or P2SH)" } (오류 문구는 Core 버전에 따라 다를 수 있음)
```

## 퀴즈
`quiz/lesson-11.md`
