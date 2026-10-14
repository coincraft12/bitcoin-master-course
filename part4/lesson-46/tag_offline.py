"""11-3 코인베이스 태그 해석 (노드 없이 실행).

data/coinbase_tags.json = bitcoin-data/mining-pools의 pools.json 원본
  ("coinbase_tags": 코인베이스에 들어가는 문자열 → 풀 이름, "payout_addresses": 보상 지급 주소 → 풀 이름)

1. 슬라이드 방식(출력 가능한 문자만 남기고 4글자 이상 첫 단어)을 제네시스 코인베이스에 적용
2. 태그 사전으로 풀 찾기 — 같은 풀이 여러 태그로 등록된 경우 세기 (슬라이드의 "한 풀이 여러 이름으로" 문제)
3. 인자로 코인베이스 hex를 주면 그 코인베이스를 해석 (getblock … 2의 tx[0].vin[0].coinbase)

    python part4/lesson-46/tag_offline.py
    python part4/lesson-46/tag_offline.py <coinbase hex> [<coinbase hex> ...]
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json, re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
POOLS = json.load(open(ROOT / "data" / "coinbase_tags.json"))
GEN = json.load(open(ROOT / "data" / "genesis_blocks.json"))


def slide_tag(cb: bytes) -> str:
    text = "".join(chr(b) if 32 <= b < 127 else " " for b in cb)
    words = [w for w in re.split(r"\s+", text) if len(w) >= 4]
    return words[0] if words else "(unknown)"


def identify_pool(cb: bytes) -> str:
    text = cb.decode("latin-1")
    hits = [(len(tag), info["name"]) for tag, info in POOLS["coinbase_tags"].items() if tag in text]
    return max(hits)[1] if hits else "(사전에 없음)"


def explain(cb: bytes):
    printable = "".join(chr(b) if 32 <= b < 127 else "·" for b in cb)
    print(f"  출력 가능 문자: {printable}")
    print(f"  슬라이드 방식 태그: {slide_tag(cb)} · 태그 사전 풀: {identify_pool(cb)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for hx in sys.argv[1:]:
            explain(bytes.fromhex(hx))
        sys.exit(0)
    print("== 1. 제네시스 코인베이스 (scriptSig) ==")
    explain(bytes.fromhex(GEN["coinbase_script_sig"]))
    tags = POOLS["coinbase_tags"]
    per_pool = Counter(info["name"] for info in tags.values())
    print("== 2. 태그 사전 ==")
    print(f"  태그 {len(tags)}개 · 풀 {len(per_pool)}곳 · 보상 지급 주소 {len(POOLS['payout_addresses'])}개")
    print(f"  태그가 2개 이상인 풀: {sum(n >= 2 for n in per_pool.values())}곳")
    for name, n in per_pool.most_common(5):
        sample = [t for t, i in tags.items() if i["name"] == name][:3]
        print(f"  {name:<16} 태그 {n}개 예: {sample}")
