import re

FILLER_WORDS = [
    "eee", "ee", "eh", "emm", "em", "anu", "nah", "nih", "kan",
    "oke", "ok", "gitu", "gini"
]

FORMAL_REPLACEMENTS = {
    "nggak": "tidak",
    "gak": "tidak",
    "ga": "tidak",
    "udah": "sudah",
    "kayak": "seperti",
    "buat": "untuk",
    "website": "situs web",
    "teman-teman": "peserta",
    "teman teman": "peserta",
    "kalian": "peserta",
    "kerjasama": "kerja sama",
}

DOMAIN_CORRECTIONS = {
    "kekijatan": "kegiatan",
    "kekiatan": "kegiatan",
    "kegijatan": "kegiatan",
    "jetual": "jadwal",
    "jadwla": "jadwal",
    "pimpinah": "pimpinan",
    "kohor": "koordinasi",
    "rapat kohor": "rapat koordinasi",
    "antarbagian": "antar bagian",
    "di fokuskan": "difokuskan",
    "membagian": "pembagian",
    "selanitun": "selanjutnya",
    "dibinta": "diminta",
    "tempat waktu": "tepat waktu",
    "renci": "rinci",
    "bertabarkan": "bertabrakan",
}

def normalize_text(text):
    if not text:
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def remove_filler_words(text):
    for word in FILLER_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text

def apply_replacements(text, replacements):
    for old, new in replacements.items():
        pattern = r"\b" + re.escape(old) + r"\b"
        text = re.sub(pattern, new, text, flags=re.IGNORECASE)
    return text

def normalize_repeated_words(text):
    return re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)

def add_basic_sentence_breaks(text):
    text = re.sub(r"\s+(lalu|selanjutnya|berikutnya|kemudian)\s+", ". ", text, flags=re.IGNORECASE)
    return text

def clean_punctuation_spacing(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"([.,!?;:])([^\s])", r"\1 \2", text)
    return text.strip()

def split_sentences(text):
    text = normalize_text(text)
    if not text:
        return []
    return re.split(r"(?<=[.!?])\s+", text)

def capitalize_sentence(sentence):
    sentence = sentence.strip()
    if not sentence:
        return ""
    return sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()

def ensure_period(sentence):
    sentence = sentence.strip()
    if sentence and sentence[-1] not in ".!?":
        sentence += "."
    return sentence

def clean_transcript(text):
    if not text or not text.strip():
        return ""

    cleaned = normalize_text(text)
    cleaned = remove_filler_words(cleaned)
    cleaned = apply_replacements(cleaned, FORMAL_REPLACEMENTS)
    cleaned = apply_replacements(cleaned, DOMAIN_CORRECTIONS)
    cleaned = normalize_repeated_words(cleaned)
    cleaned = add_basic_sentence_breaks(cleaned)
    cleaned = clean_punctuation_spacing(cleaned)

    sentences = split_sentences(cleaned)

    final_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence.split()) <= 2:
            continue
        sentence = ensure_period(sentence)
        sentence = capitalize_sentence(sentence)
        final_sentences.append(sentence)

    if not final_sentences:
        cleaned = ensure_period(cleaned)
        cleaned = capitalize_sentence(cleaned)
        return cleaned

    return " ".join(final_sentences)