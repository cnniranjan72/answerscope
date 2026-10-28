"""Deterministic prompt categories inferred from the question text (no production
labels are supplied). Two axes: branded/unbranded, and one intent topic chosen by the
first matching rule in priority order. Changing any rule requires a version bump."""
from __future__ import annotations

import re

from app.services.text import BRAND_RE

CATEGORY_VERSION = "cat-v1"

# (category, pattern) in priority order; the first match wins.
TOPIC_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("comparison", re.compile(
        r"\b(better than|compare[ds]?|vs\.?|versus|alternatives?|prefer|faster than|"
        r"profound|peec|otterly|athenahq|dageno)\b", re.I)),
    ("pricing_terms", re.compile(
        r"\b(cost|costs|price|pricing|overpriced|worth|retainers?|cancel|fees?|value)\b", re.I)),
    ("onboarding_access", re.compile(
        r"\b(set ?up|onboarding|sign up|self serve|how fast|how long|integrations?|turnkey|"
        r"outside the us|available)\b", re.I)),
    ("trust_efficacy", re.compile(
        r"\b(legit|trustworthy|safe|hype|gimmick|actually|effective|results|skeptical|"
        r"empty promises|prompt hacks|tricks|spamming|unpredictable|real .* users|"
        r"doesn't increase)\b", re.I)),
]
DEFAULT_TOPIC = "capability_fit"
TOPICS = [name for name, _ in TOPIC_RULES] + [DEFAULT_TOPIC]


def is_branded(prompt_text: str) -> bool:
    return bool(BRAND_RE.search(prompt_text))


def topic(prompt_text: str) -> str:
    for name, pattern in TOPIC_RULES:
        if pattern.search(prompt_text):
            return name
    return DEFAULT_TOPIC
