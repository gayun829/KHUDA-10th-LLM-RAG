"""출력 줄 맞추기 도우미 (한글은 화면에서 두 칸을 차지한다). 읽지 않아도 됩니다."""
import unicodedata


def width(s):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def pad(s, w, right=False):
    s = str(s)
    gap = " " * max(0, w - width(s))
    return gap + s if right else s + gap


def short(s, w):
    """화면 폭 w칸을 넘으면 잘라서 '…'를 붙인다"""
    s = str(s).replace("\n", " ")
    if width(s) <= w:
        return s
    out = ""
    for ch in s:
        if width(out + ch) > w - 1:
            break
        out += ch
    return out + "…"


def mark(ok):
    return "✓" if ok else "✗  ← TODO를 확인하세요"
