def summarize_text(text, max_sentences=3):
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    summary = ". ".join(sentences[:max_sentences])

    if summary and not summary.endswith("."):
        summary += "."

    return summary