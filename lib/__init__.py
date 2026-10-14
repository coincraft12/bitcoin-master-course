"""lib 패키지. 가져오는 순간 표준 출력이 UTF-8이 되도록 맞춘다.

Windows에서 출력을 파일·파이프로 돌리면 stdout이 cp949가 되어 − ≈ ‖ — 같은 기호를 찍을 때
UnicodeEncodeError가 난다. 슬라이드의 기대 출력을 그대로 두려고 코드 대신 여기서 한 번 고친다.
"""
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        if (getattr(_s, "encoding", None) or "").lower().replace("-", "") != "utf8":
            _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
