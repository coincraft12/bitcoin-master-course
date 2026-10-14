"""12-1 실습 보조: 유사 주소 비교·탐지 (s121-lab, s121-threats1 "주소록·전체 대조").

address_poisoning.py가 보여 준 공격을 막는 쪽의 도구다.
  - short(): 지갑 앱처럼 앞 8자·뒤 4자만 줄여 보여 준다 → 사람이 구별하기 어렵다.
  - diff_marks(): 두 주소를 한 글자씩 대조해 다른 자리를 ^로 표시한다 → 전체 대조.
  - find_lookalikes(): 주소록(신뢰 주소)과 앞뒤 끝 글자가 여러 개 같지만 전체는 다른 후보를 찾는다
    ("bcrt1q"처럼 모두에게 같은 앞부분은 세지 않는다. 기본 3글자 이상이면 경고).

    python part5/lesson-49/detect_poison.py demo            # 슬라이드의 두 주소로 비교 (결정적)
    python part5/lesson-49/detect_poison.py search          # 새로 2글자짜리 가짜 주소를 찾아 비교 (몇 초)
    python part5/lesson-49/detect_poison.py check 주소록.txt 후보주소 [후보주소 ...]

주소록 파일은 한 줄에 주소 하나(# 뒤는 주석). 교육 목적. 실제 주소를 대상으로 가짜 주소를 만들지 말 것.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import time
from lib.keys import new_private_key, public_key, ser_compressed, p2wpkh_address


def short(a: str, head: int = 8, tail: int = 4) -> str:
    """지갑 화면처럼 줄여 쓴 형태. 예: bcrt1qzw…ury4"""
    return f"{a[:head]}…{a[-tail:]}"


def diff_marks(a: str, b: str) -> str:
    """같은 길이의 두 주소에서 다른 글자 자리에 ^, 같은 자리에 공백."""
    n = max(len(a), len(b))
    return "".join(" " if i < len(a) and i < len(b) and a[i] == b[i] else "^" for i in range(n))


def fixed_len(a: str) -> int:
    """누구 주소나 같은 앞부분 길이: HRP + "1" + witness 버전 글자 (예: "bcrt1q" → 6)."""
    return a.rfind("1") + 2


def edge_match(trusted: str, cand: str) -> tuple:
    """(고정부 뒤 앞쪽 일치 글자 수, 뒤쪽 일치 글자 수)."""
    f = fixed_len(trusted)
    if cand[:f] != trusted[:f]:
        return (0, 0)
    pre = 0
    while f + pre < min(len(trusted), len(cand)) and trusted[f + pre] == cand[f + pre]:
        pre += 1
    suf = 0
    while suf < min(len(trusted), len(cand)) - f and trusted[-1 - suf] == cand[-1 - suf]:
        suf += 1
    return (pre, suf)


def is_lookalike(trusted: str, cand: str, min_chars: int = 3) -> bool:
    """전체는 다른데 앞뒤 끝에서 맞는 글자가 min_chars개 이상이면 중독 의심.
    무작위 주소 둘이 앞뒤 합쳐 3글자 이상 우연히 맞을 확률은 수천 분의 1 수준이다."""
    if cand == trusted:
        return False
    pre, suf = edge_match(trusted, cand)
    return pre + suf >= min_chars


def find_lookalikes(book: list, candidates: list, min_chars: int = 3) -> list:
    """(후보, 닮은 신뢰 주소) 목록. 주소록에 그대로 있는 후보는 안전으로 본다."""
    hits = []
    for c in candidates:
        if c in book:
            continue
        for t in book:
            if is_lookalike(t, c, min_chars):
                hits.append((c, t))
    return hits


def _addr() -> str:
    return p2wpkh_address(ser_compressed(public_key(new_private_key())), hrp="bcrt")


# s121-lab 슬라이드에 나온 실행 예 (피해자 주소, 찾아낸 가짜 주소)
SLIDE_VICTIM = "bcrt1qzws2nuwwpwwkq69hpgt9ncuyj4k6y46fjlury4"
SLIDE_FAKE = "bcrt1qzwmgzg8wvh06c9f2tyhjrhhnyy54tsttgzjc34"


def show_pair(trusted: str, other: str):
    print("[줄여 보기] 지갑 화면처럼 앞 8자·뒤 4자만")
    print("    " + short(trusted) + "   ← 주소록")
    print("    " + short(other) + "   ← 거래 내역")
    print("[전체 대조] ^ = 다른 글자")
    print("    " + trusted + "   ← 주소록")
    print("    " + other + "   ← 거래 내역")
    print("    " + diff_marks(trusted, other))
    pre, suf = edge_match(trusted, other)
    verdict = "중독 의심" if is_lookalike(trusted, other, 2) else "닮지 않음"
    print(f"[탐지] 고정부(bcrt1q) 뒤 앞 {pre}자·끝 {suf}자 일치 → {verdict}")


def demo():
    """슬라이드의 두 주소로 줄여 보기와 전체 대조를 비교한다 (결정적)."""
    show_pair(SLIDE_VICTIM, SLIDE_FAKE)


def search():
    """새 피해자 주소를 만들고, 고정부 뒤 1자·끝 1자가 같은 가짜 주소를 찾는다 (기대 32² = 1,024번, 몇 초).
    address_poisoning.py(3글자, 평균 4~5분)를 기다리기 어려울 때 쓴다."""
    victim = _addr()
    t0, tries = time.time(), 0
    while True:
        tries += 1
        fake = _addr()
        if fake[:7] == victim[:7] and fake[-1] == victim[-1]:
            break
    print(f"시도: {tries}번, {time.time() - t0:.1f}초")
    show_pair(victim, fake)


def check(book_file: str, candidates: list):
    """주소록과 후보 주소들을 대조해 안전/경고/미확인을 출력. 경고가 있으면 1을 돌려준다."""
    book = []
    for line in open(book_file, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            book.append(line)
    hits = find_lookalikes(book, candidates)
    for c in candidates:
        if c in book:
            print(f"안전  {c}  (주소록에 있음)")
        elif any(h[0] == c for h in hits):
            t = next(h[1] for h in hits if h[0] == c)
            pre, suf = edge_match(t, c)
            print(f"경고  {c}  (주소록 주소와 앞 {pre}자·뒤 {suf}자가 같지만 다른 주소)")
            print(f"      {t}  ← 주소록")
            print("      " + diff_marks(t, c))
        else:
            print(f"미확인 {c}  (주소록에 없음 — 출처를 따로 확인)")
    return 1 if hits else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        demo()
    elif len(sys.argv) >= 2 and sys.argv[1] == "search":
        search()
    elif len(sys.argv) >= 4 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2], sys.argv[3:]))
    else:
        sys.exit(__doc__)
