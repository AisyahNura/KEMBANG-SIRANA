import re

FILLER_WORDS = [
    "eee", "eh", "emm", "anu", "jadi gini", "gitu", "kan", "nih", "nah", "oke"
]

def clean_transcript(text):
    cleaned = text

    for filler in FILLER_WORDS:
        pattern = r"\b" + re.escape(filler) + r"\b"
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned