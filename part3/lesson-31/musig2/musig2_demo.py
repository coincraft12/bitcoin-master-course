"""7-4 s74-musig: MuSig2(BIP327) 원리 실습 — 참조 구현으로 2-of-2 키 집계 → 2라운드 서명 → 집계 서명을 우리 lib으로 검증.

reference.py와 vectors/는 bitcoin/bips 저장소 bip-0327의 원본 그대로다(BSD-3-Clause). 공식 벡터 확인: python reference.py
s74-caveat: "원리 실습은 BIP327 참조 구현으로". 논스는 재현을 위해 고정 rand를 쓴다 — 실제로는 서명마다 새 난수, 논스 재사용 금지(7-2).
고정 예제 키 · 실제 자금에 쓰지 말 것.

    python part3/lesson-31/musig2/musig2_demo.py
"""
import sys, pathlib, hashlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE))
import reference as m                                   # BIP327 참조 구현
from lib.taproot import output_key, tagged_hash
from lib.keys import p2tr_address
from lib import schnorr

sk1 = hashlib.sha256(b"musig2 demo signer 1").digest()
sk2 = hashlib.sha256(b"musig2 demo signer 2").digest()
pk1, pk2 = m.individual_pk(sk1), m.individual_pk(sk2)
pubkeys = m.key_sort([pk1, pk2])

# 키 집계: 각 공개키에 "전체 키 목록에 의존하는 계수"를 곱해 더한다 → rogue key 방지
ctx = m.key_agg(pubkeys)
agg = m.get_xonly_pk(ctx)
print("참여자 공개키 :", pk1.hex()[:18] + "…", pk2.hex()[:18] + "…")
print("집계 x-only 키:", agg.hex())

# 6-4 키 경로처럼 BIP86 조정(머클 루트 없음)을 집계키에 적용 → 출력키 Q
t = tagged_hash("TapTweak", agg)
Q = output_key(agg)
print("출력키 Q      :", Q.hex(), "· 주소", p2tr_address(Q, hrp="bcrt"))

msg = hashlib.sha256(b"musig2 demo sighash").digest()   # 실제로는 7-4 taproot_sighash 결과
# 1라운드: 각자 공개 논스(점 2개) 교환 — 메시지를 알기 전에 미리 해도 된다
sec1, pub1 = m.nonce_gen_internal(bytes([1]) * 32, sk1, pk1, agg, msg, None)
sec2, pub2 = m.nonce_gen_internal(bytes([2]) * 32, sk2, pk2, agg, msg, None)
aggnonce = m.nonce_agg([pub1, pub2])
session = m.SessionContext(aggnonce, pubkeys, [t], [True], msg)
# 2라운드: 각자 부분 서명
psig1 = m.sign(sec1, sk1, session)
psig2 = m.sign(sec2, sk2, session)
print("부분 서명 검증:", m.partial_sig_verify_internal(psig1, pub1, pk1, session),
      m.partial_sig_verify_internal(psig2, pub2, pk2, session))
# 집계: 출력키 Q에 대한 보통의 BIP340 서명 하나
sig = m.partial_sig_agg([psig1, psig2], session)
print("집계 서명 64B :", sig.hex())
print("lib/schnorr.verify(msg, Q, sig):", schnorr.verify(msg, Q, sig))
print("→ 키 경로 witness는 [64B 서명] 하나. 단일 서명 지갑과 구분할 수 없다 (6-4).")
sys.path.insert(0, str(HERE.parent.parent / "lesson-27" / "assignment" / "solution"))
from solution_inheritance import REC, descriptor, address, BLOCKS     # 6강 미니 과제 정답
print("\n6강 과제의 자리표시 키를 이 집계키로 바꾸면 (복구 키는 그대로):")
print(" ", descriptor(agg, REC, BLOCKS))
print("  주소", address(agg, REC, BLOCKS))
