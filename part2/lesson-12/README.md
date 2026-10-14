# lesson-12 · 3-4 SegWit 주소: bech32, P2WPKH, P2WSH, 중첩 SegWit

## 목표
- bech32 주소(HRP · 구분자 1 · witness 버전 · 프로그램 · 체크섬 6글자)의 구성과 Base58 대비 장점을 설명한다.
- P2WPKH 주소를 직접 계산하고 Core와 대조한다.
- P2WSH(32B, SHA256)와 중첩 SegWit(P2SH-P2WPKH)의 용도를 설명한다.

## 만드는 코드
- `lib/segwit_addr.py` — BIP173·BIP350 Python 참조 구현(MIT) 그대로: `encode(hrp, witver, witprog)`, `decode(hrp, addr)`, `bech32_encode`, `bech32_decode`, `convertbits`, `Encoding`
- `lib/keys.py` — `p2wpkh_address(pubkey_compressed, hrp="bc")`, `p2wsh_address(witness_script, hrp="bc")`, `p2sh_p2wpkh_address(pubkey_compressed, version=0x05)`

HRP: `bc` mainnet · `tb` testnet·signet · `bcrt` regtest. 잠금 스크립트는 `0x00 0x14 ‖ 20바이트`(P2WPKH), `0x00 0x20 ‖ 32바이트`(P2WSH).

## 실습 순서
1. `segwit_address.py`로 개인키 1(송금 금지)의 SegWit 주소와 오류 실험
2. Core `getnewaddress "" bech32` → `getaddressinfo`의 pubkey, witness_version, witness_program 대조 (hrp를 `bcrt`로!)
3. 같은 공개키로 `p2sh_p2wpkh_address(…, 0xc4)` → 2로 시작하는지, `getnewaddress "" p2sh-segwit`과 형태 비교
4. 한 글자 변경 / 대소문자 혼합 / 전부 대문자로 디코딩·`validateaddress`

## 실행
```bash
python part2/lesson-12/segwit_address.py
python part2/lesson-12/check_core_bech32.py 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798 bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080 751e76e8199196d454941c45d1b3a323f1433bd6
bash   part2/lesson-12/core_bech32.sh          # regtest 노드 필요
```

## 기대 출력
`segwit_address.py` (결정적)
```
[개인키 1의 SegWit 주소]
P2WPKH mainnet      : bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
P2WPKH regtest      : bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
hash160 = 프로그램  : 751e76e8199196d454941c45d1b3a323f1433bd6
P2SH-P2WPKH mainnet : 3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN
P2SH-P2WPKH regtest : 2NAUYAHhujozruyzpsFRP63mbrdaU5wnEpN
P2WSH testnet       : tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7 (62자)
P2WPKH 길이         : 42 자

[오류 실험] bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
원래            : 0 751e76e8199196d454941c45d1b3a323f1433bd6
한 글자 변경    : (None, None) bc1qw508d6qejxtdg4y5q3zarvary0c5xw7kv8f3t4
대소문자 혼합   : (None, None) bc1qw508d6qeJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4
전부 대문자     : True BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4
hrp를 bcrt로    : (None, None)
```
P2WPKH mainnet 주소와 P2WSH testnet 주소는 BIP173 문서의 테스트 벡터와 같다.

`check_core_bech32.py` (위 인자, 결정적)
```
p2wpkh_address(hrp=bcrt) : bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
Core 주소                : bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
주소 일치                : True
hash160 == program       : True
hrp=bc로 잘못 계산하면   : bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
p2sh_p2wpkh(0xc4)        : 2NAUYAHhujozruyzpsFRP63mbrdaU5wnEpN
```
`core_bech32.sh` — 값은 실행마다 다르다. `주소 일치 : True`, `hash160 == program : True`, 오류 실험 세 줄은 순서대로 `isvalid` false · false · true.
```
{ "pubkey": "033d92398bc02d76bec0c763f917631e369d1c41bb919e60ac8b31c006410b04c5", "witness_version": 0, "witness_program": "5262688049f050fc48cec78fa55779b2f3b94ca5" } (실행마다 다름)
p2wpkh_address(hrp=bcrt) : bcrt1q2f3x3qzf7pg0cjxwc78624mektemjn99vrymxu (실행마다 다름)
…
Core p2sh-segwit 주소 (2로 시작):
2Mz4gb7PhAmihTmczuVUPJ8oh5S41p6q3Uf (실행마다 다름)
```

## 퀴즈
`quiz/lesson-12.md`
