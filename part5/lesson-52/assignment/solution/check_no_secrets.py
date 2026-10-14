"""12강 미니 과제 제출 전 점검: 문서에 실제 키 정보가 들어 있지 않은가 (s12-assign, s124-doc).

"위치와 절차는 쓰고, 비밀은 쓰지 않는다." 다음을 찾아 알려 준다.
  금지  니모닉(BIP39 단어가 12개 이상 연속), 확장 개인키(xprv·tprv 등), WIF 개인키
  금지  실제 주소 (bech32/bech32m, base58check 주소) — 체크섬까지 맞는 것만
  주의  확장 공개키(xpub·tpub): 비밀은 아니지만 실제 지갑이면 모든 주소·잔액이 드러난다
  주의  "패스프레이즈: 값" 형태의 줄

    python part5/lesson-52/assignment/solution/check_no_secrets.py 내_설계.md

금지 항목이 하나라도 있으면 종료 코드 1. 이 점검은 보조 수단일 뿐, 사람이 다시 읽어야 한다.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
import re
from lib.bip39 import WORDS
from lib.base58 import b58check_decode
from lib import segwit_addr

WORDSET = set(WORDS)
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
EXT_PRV = ("xprv", "tprv", "yprv", "zprv", "uprv", "vprv")
EXT_PUB = ("xpub", "tpub", "ypub", "zpub", "upub", "vpub")


def b58check_ok(s: str) -> bytes:
    try:
        return b58check_decode(s)
    except ValueError:
        return b""


def find_mnemonics(text: str, min_words: int = 12) -> list:
    """BIP39 영어 단어가 min_words개 이상 이어진 구간."""
    toks = re.findall(r"[A-Za-z]+", text)
    hits, run = [], []
    for t in toks + [""]:
        if t.lower() in WORDSET:
            run.append(t.lower())
            continue
        if len(run) >= min_words:
            hits.append(" ".join(run[:3]) + " … (" + str(len(run)) + "단어)")
        run = []
    return hits


def scan(text: str) -> list:
    """[(등급, 설명)] — 등급은 '금지' 또는 '주의'."""
    out = [("금지", f"니모닉으로 보이는 단어열: {m}") for m in find_mnemonics(text)]
    for tok in re.findall(rf"[{B58}]{{26,120}}", text):
        raw = b58check_ok(tok)
        if not raw:
            continue
        if tok[:4] in EXT_PRV:
            out.append(("금지", f"확장 개인키 {tok[:12]}…"))
        elif tok[:4] in EXT_PUB:
            out.append(("주의", f"확장 공개키 {tok[:12]}… (실제 지갑이면 빼거나 가린다)"))
        elif len(raw) in (33, 34) and raw[0] in (0x80, 0xEF):
            out.append(("금지", f"WIF 개인키 {tok[:6]}…"))
        elif len(raw) == 21 and raw[0] in (0x00, 0x05, 0x6F, 0xC4):
            out.append(("금지", f"주소 {tok}"))
    for tok in re.findall(r"\b(?:bc|tb|bcrt)1[02-9ac-hj-np-z]{8,87}\b", text, flags=re.I):
        hrp = tok.lower().rsplit("1", 1)[0]
        if segwit_addr.decode(hrp, tok.lower())[0] is not None:
            out.append(("금지", f"주소 {tok}"))
    for line in text.splitlines():
        if re.search(r"(passphrase|패스프레이즈)\s*[:=]\s*\S{4,}", line, flags=re.I):
            out.append(("주의", f"패스프레이즈 값으로 보이는 줄: {line.strip()[:40]}"))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    found = scan(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    for level, msg in found:
        print(f"[{level}] {msg}")
    banned = [f for f in found if f[0] == "금지"]
    print(f"금지 {len(banned)}건, 주의 {len(found) - len(banned)}건")
    if banned:
        print("→ 제출하지 않는다. 비밀은 지우고 '위치'만 남긴다.")
        sys.exit(1)
    print("→ 실제 키 정보가 보이지 않는다. 그래도 한 번 더 직접 읽어 본다.")


if __name__ == "__main__":
    main()
