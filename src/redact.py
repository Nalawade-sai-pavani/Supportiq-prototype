"""Step 1 of pipeline: mask personal data before any model sees the text."""
import re

PATTERNS = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "PHONE": re.compile(r"\+?\d[\d\s().-]{8,}\d"),
    "ORDER_ID": re.compile(r"#\d{3,}"),
}

def redact(text: str) -> str:
    # order matters: cards before phones so long digit runs are labelled correctly
    for label in ["EMAIL", "CARD", "PHONE", "ORDER_ID"]:
        text = PATTERNS[label].sub(f"[{label}]", text)
    return text
