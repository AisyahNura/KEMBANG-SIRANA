import os
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)

# =========================
# OPENAI FALLBACK
# =========================
def summarize_with_openai(text):
    """Fallback ke OpenAI jika HuggingFace gagal"""
    if not OPENAI_API_KEY:
        return None

    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Anda adalah asisten yang ahli dalam membuat ringkasan rapat dalam Bahasa Indonesia."},
                {"role": "user", "content": f"Ringkas teks rapat berikut menjadi ringkasan yang singkat, jelas, dan formal dalam Bahasa Indonesia:\n\n{text}"}
            ],
            max_tokens=300,
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        return normalize_text(summary)

    except Exception as e:
        print(f"OpenAI fallback failed: {e}")
        return None
def normalize_text(text):
    if not text:
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def split_sentences(text):
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

# =========================
# FALLBACK (AMAN)
# =========================
def fallback_summary(text, max_sentences=3):
    sentences = split_sentences(text)
    if sentences:
        summary = " ".join(sentences[:max_sentences])
        if summary:
            return summary

    words = text.split()
    if not words:
        return "Tidak ada teks untuk diringkas."

    return " ".join(words[:min(len(words), 30)]) + ("..." if len(words) > 30 else "")

# =========================
# SPLIT TEXT PANJANG
# =========================
def chunk_text(text, max_chars=2500):
    text = normalize_text(text)

    if len(text) <= max_chars:
        return [text]

    sentences = split_sentences(text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks

# =========================
# CORE SUMMARY (UPGRADE)
# =========================
def summarize_once(text):
    text = normalize_text(text)

    if not text:
        return "Tidak ada teks untuk diringkas."

    try:
        print("Memulai proses ringkasan...")

        # Untuk model summarization Hugging Face, kirimkan teks asli tanpa instruksi tambahan.
        result = client.summarization(
            text,
            model="facebook/bart-large-cnn"
        )

        # Jika gagal dengan model pertama, coba model lain
        if not result or (hasattr(result, 'summary_text') and not result.summary_text):
            print("Model pertama gagal, mencoba model alternatif...")
            try:
                result = client.summarization(
                    text,
                    model="sshleifer/distilbart-cnn-12-6"  # Model alternatif yang lebih ringan
                )
            except Exception as e:
                print(f"Model alternatif gagal: {e}")
                pass

        print("Ringkasan selesai diproses")
        print(f"Raw result type: {type(result)}")
        print(f"Raw result: {result}")

        # Jika result kosong atau tidak valid, gunakan fallback
        if not result:
            print("Result kosong, menggunakan fallback")
            return fallback_summary(text)

        # ambil hasil
        if hasattr(result, "summary_text") and result.summary_text:
            summary = normalize_text(result.summary_text)
        elif isinstance(result, dict) and "summary_text" in result:
            summary = normalize_text(result["summary_text"])
        elif isinstance(result, dict) and "generated_text" in result:
            summary = normalize_text(result["generated_text"])
        elif isinstance(result, dict) and "text" in result:
            summary = normalize_text(result["text"])
        elif isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, dict) and "summary_text" in first:
                summary = normalize_text(first["summary_text"])
            elif isinstance(first, dict) and "generated_text" in first:
                summary = normalize_text(first["generated_text"])
            elif isinstance(first, dict) and "text" in first:
                summary = normalize_text(first["text"])
            else:
                return fallback_summary(text)
        else:
            return fallback_summary(text)

        # Bersihkan output - hapus prompt yang ikut tercetak
        prompt_prefix = "Ringkas teks rapat berikut menjadi ringkasan yang singkat, jelas, dan formal dalam Bahasa Indonesia:"
        if summary.startswith(prompt_prefix):
            summary = summary[len(prompt_prefix):].strip()

        # Hapus juga teks asli yang mungkin ikut
        if text in summary:
            summary = summary.replace(text, "").strip()

        # Jika masih mengandung prompt atau terlalu panjang (mungkin keseluruhan input), ekstrak hanya bagian akhir
        if len(summary) > len(text) * 2:  # Jika output jauh lebih panjang dari input
            # Ambil hanya bagian terakhir setelah titik atau baris baru
            sentences = summary.split('.')
            if len(sentences) > 1:
                summary = '.'.join(sentences[-2:])  # Ambil 2 kalimat terakhir
            else:
                # Ambil setelah baris baru terakhir
                lines = summary.split('\n')
                summary = lines[-1] if lines else summary

        # Bersihkan karakter khusus di awal/akhir
        summary = summary.strip(".: \n\t")

        print(f"Cleaned summary: '{summary}'")

        # kalau terlalu pendek / aneh
        if len(summary) < 15:
            return fallback_summary(text)

        return summary

    except Exception as e:
        print("Error summary:", e)
        # Coba OpenAI sebagai fallback
        openai_result = summarize_with_openai(text)
        if openai_result:
            print("Berhasil menggunakan OpenAI fallback")
            return openai_result

        return fallback_summary(text)

# =========================
# FINAL SUMMARY
# =========================
def summarize_text(text):
    text = normalize_text(text)

    if not text:
        return "Tidak ada teks untuk diringkas."

    # split kalau panjang
    chunks = chunk_text(text)

    # kalau pendek
    if len(chunks) == 1:
        return summarize_once(chunks[0])

    # kalau panjang → ringkas per bagian dulu
    partial_summaries = []
    for chunk in chunks:
        partial = summarize_once(chunk)
        partial_summaries.append(partial)

    # gabungkan lalu ringkas lagi
    combined = " ".join(partial_summaries)
    final_summary = summarize_once(combined)

    return final_summary if final_summary else fallback_summary(combined)