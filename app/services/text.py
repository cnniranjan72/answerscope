"""Answer-text handling: separating the appended citation list from the answer body,
brand detection, and locating evidence excerpts at exact source offsets."""
from __future__ import annotations

import re
import unicodedata

BRAND = "Kasparro"
BRAND_RE = re.compile(r"\bkasparro\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+")
CITATION_BLOCK_MARKER = "\n\nCitations:\n"

_TRANSLATE = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ", " ": " ",
})
_DROP = set("*_`#>")


def answer_body(answer_text: str) -> str:
    """answer_text = answer body + an appended 'Citations:' list of URLs (see data/READ_ME.txt).
    The URL list is analysed separately from citations.jsonl, so it is excluded here: a
    brand URL in that list is a citation, not a mention in the answer."""
    idx = answer_text.rfind(CITATION_BLOCK_MARKER)
    if idx == -1:
        return answer_text
    tail = answer_text[idx + len(CITATION_BLOCK_MARKER):]
    if all(re.match(r"^\[\d+\]\s+\S+", ln) for ln in tail.strip().splitlines() if ln.strip()):
        return answer_text[:idx]
    return answer_text


def brand_mention_offsets(body: str) -> list[int]:
    """Offsets of the brand name in the body, ignoring occurrences inside URLs."""
    url_spans = [m.span() for m in URL_RE.finditer(body)]
    return [m.start() for m in BRAND_RE.finditer(body)
            if not any(a <= m.start() < b for a, b in url_spans)]


def _normalise_with_map(text: str) -> tuple[str, list[int]]:
    """Lower-case, unify quotes/dashes, drop markdown emphasis characters and collapse
    whitespace, keeping a map from each normalised character to its source offset."""
    out: list[str] = []
    idx: list[int] = []
    prev_space = True
    for i, ch in enumerate(text):
        ch = unicodedata.normalize("NFKC", ch).translate(_TRANSLATE)
        if not ch or ch in _DROP:
            continue
        for c in ch:
            if c.isspace():
                if prev_space:
                    continue
                out.append(" ")
                idx.append(i)
                prev_space = True
            else:
                out.append(c.lower())
                idx.append(i)
                prev_space = False
    return "".join(out), idx


def normalise(text: str) -> str:
    return _normalise_with_map(text)[0].strip()


def locate(excerpt: str, body: str) -> tuple[int, int] | None:
    """Return (start, end) source offsets of excerpt in body, tolerant only of markdown
    emphasis, quote/dash style and whitespace. Anything else must match exactly."""
    needle = normalise(excerpt)
    if len(needle) < 3:
        return None
    hay, idx = _normalise_with_map(body)
    pos = hay.find(needle)
    if pos == -1:
        return None
    return idx[pos], idx[pos + len(needle) - 1] + 1


def contains_name(name: str, body: str) -> bool:
    """Whole-word, case-insensitive name match. Unlike locate(), it has no minimum length,
    so short real names such as 'G2' are accepted (regression: failure F1)."""
    needle = normalise(name)
    if not needle:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])", normalise(body)) is not None
