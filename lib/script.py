"""교육용 구현. 실제 자금에 쓰지 말 것.

Script 디코더와 간이 실행기 (6-1 s61-code1~3 슬라이드 그대로).

    from lib.script import parse_script, run
    run(script_sig, script_pubkey)                       # checksig는 기본값(항상 참)
    run(script_sig, script_pubkey, checksig=my_check)    # 7강: ECDSA + sighash로 진짜 검증

- 두 스크립트를 따로 파싱해 차례로 실행하고 스택만 이어받는다(2010년 버그 이후 규칙).
- OPS에 있는 opcode만 실행한다. 나머지는 NotImplementedError (교육용 축소판).
- 음수 0 규칙 등은 생략했다. 실제 검증은 Bitcoin Core의 인터프리터가 기준이다.
"""
from lib.hashes import hash160, sha256

OPS = {0x00: "OP_0", 0x63: "OP_IF", 0x67: "OP_ELSE", 0x68: "OP_ENDIF",
       0x69: "OP_VERIFY", 0x6a: "OP_RETURN", 0x76: "OP_DUP", 0x87: "OP_EQUAL",
       0x88: "OP_EQUALVERIFY", 0xa8: "OP_SHA256", 0xa9: "OP_HASH160", 0xac: "OP_CHECKSIG"}


def parse_script(b: bytes) -> list:
    i, out = 0, []
    while i < len(b):
        op = b[i]; i += 1
        if 0x01 <= op <= 0x4b:
            out.append(b[i:i+op]); i += op
        elif op == 0x4c:                      # OP_PUSHDATA1
            n = b[i]; i += 1
            out.append(b[i:i+n]); i += n
        else:
            out.append(OPS.get(op, f"OP_UNKNOWN_{op:#04x}"))
    return out


def is_true(v: bytes) -> bool:
    return any(v)                             # 단순화: 음수 0 규칙 생략


def run(script_sig, script_pubkey, checksig=lambda sig, pub: True, trace=True):
    stack = []
    for script in (script_sig, script_pubkey):   # 분리 실행, 스택만 이어받음
        for item in parse_script(script):
            if isinstance(item, bytes): stack.append(item)
            elif item == "OP_0": stack.append(b"")
            elif item == "OP_DUP": stack.append(stack[-1])
            elif item == "OP_HASH160": stack.append(hash160(stack.pop()))
            elif item == "OP_SHA256": stack.append(sha256(stack.pop()))
            elif item in ("OP_EQUAL", "OP_EQUALVERIFY"):
                a, b = stack.pop(), stack.pop()
                if item == "OP_EQUALVERIFY":
                    if a != b: return False
                else: stack.append(b"\x01" if a == b else b"")
            elif item == "OP_VERIFY":
                if not is_true(stack.pop()): return False
            elif item == "OP_CHECKSIG":
                pub, sig = stack.pop(), stack.pop()
                stack.append(b"\x01" if checksig(sig, pub) else b"")
            elif item == "OP_RETURN": return False
            else: raise NotImplementedError(item)
            if trace:
                name = item if isinstance(item, str) else f"PUSH {len(item)}B"
                print(f"{name:<16}| " + " ".join(x.hex()[:8] or "''" for x in stack))
    return bool(stack) and is_true(stack[-1])
