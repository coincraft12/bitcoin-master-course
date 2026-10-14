"""3-4 실습: P2WPKH·P2WSH·중첩 SegWit 주소 계산과 bech32 오류 실험 (s34-code).

실행: python part2/lesson-12/segwit_address.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib import segwit_addr
from lib.ec import G
from lib.hashes import hash160
from lib.keys import ser_compressed, p2wpkh_address, p2wsh_address, p2sh_p2wpkh_address

pub = ser_compressed(G)                       # 개인키 1 — 송금 금지
print("[개인키 1의 SegWit 주소]")
print("P2WPKH mainnet      :", p2wpkh_address(pub))
print("P2WPKH regtest      :", p2wpkh_address(pub, hrp="bcrt"))
print("hash160 = 프로그램  :", hash160(pub).hex())
print("P2SH-P2WPKH mainnet :", p2sh_p2wpkh_address(pub))
print("P2SH-P2WPKH regtest :", p2sh_p2wpkh_address(pub, 0xc4))
ws = bytes([0x21]) + pub + b"\xac"            # witness script: <공개키> OP_CHECKSIG
print("P2WSH testnet       :", p2wsh_address(ws, hrp="tb"), f"({len(p2wsh_address(ws))}자)")
print("P2WPKH 길이         :", len(p2wpkh_address(pub)), "자")

addr = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"   # BIP173 테스트 벡터
print("\n[오류 실험]", addr)
ver, prog = segwit_addr.decode("bc", addr)
print("원래            :", ver, bytes(prog).hex())
i = 20
one = addr[:i] + ("q" if addr[i] != "q" else "p") + addr[i + 1:]
print("한 글자 변경    :", segwit_addr.decode("bc", one), one)
mixed = addr[:12] + addr[12:].upper()
print("대소문자 혼합   :", segwit_addr.decode("bc", mixed), mixed)
print("전부 대문자     :", segwit_addr.decode("bc", addr.upper())[0] is not None, addr.upper())
print("hrp를 bcrt로    :", segwit_addr.decode("bcrt", addr))
