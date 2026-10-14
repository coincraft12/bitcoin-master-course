"""12-1 실습: 주소 중독이 얼마나 쉬운가 (s121-lab).

피해자 주소와 앞 8글자("bcrt1q" + 2글자)·끝 1글자가 같은 가짜 주소를
무작위 키 생성만으로 찾는다. 맞출 글자 3개 → 기대 시도 32³ = 32,768번.
교육 목적. 실제 주소를 대상으로 쓰지 말 것.

    python part5/lesson-49/address_poisoning.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib.keys import new_private_key, public_key, ser_compressed, p2wpkh_address
def addr(): return p2wpkh_address(ser_compressed(public_key(new_private_key())), hrp="bcrt")
victim = addr()
head, tail = victim[:8], victim[-1:]     # "bcrt1q" + 2글자, 끝 1글자
tries = 0
while True:
    tries += 1
    fake = addr()
    if fake.startswith(head) and fake.endswith(tail): break
print(victim); print(fake); print("시도:", tries)
