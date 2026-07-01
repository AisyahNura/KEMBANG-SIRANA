import os
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)

# =========================
# GROQ SUMMARIZATION
# =========================
def summarize_with_groq(text):
    """Meringkas teks menggunakan Groq Llama-3.1-8b-instant"""
    if not GROQ_API_KEY:
        return None

    try:
        from openai import OpenAI
        groq_client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        print("Menghubungi Groq API untuk membuat ringkasan rapat terstruktur...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Anda adalah asisten notulen rapat profesional. "
                        "Buat ringkasan rapat (Notulensi) dalam Bahasa Indonesia yang formal, padat, "
                        "dan mudah dipahami. Tuliskan ringkasan dalam format terstruktur berikut secara singkat:\n\n"
                        "**Poin Penting:**\n(Tuliskan 1-2 poin pembahasan utama rapat secara singkat)\n\n"
                        "**Kesimpulan:**\n(Tuliskan kesimpulan rapat secara singkat)\n\n"
                        "PENTING: Jangan gunakan simbol heading Markdown (seperti ### atau #), jangan gunakan bullet points (seperti - atau *), dan jangan gunakan emoji apa pun di dalam teks Anda. "
                        "Jika ada kesalahan ketik atau salah dengar kecil pada transkrip, perbaiki secara wajar berdasarkan konteks."
                    )
                },
                {"role": "user", "content": f"Berikut adalah transkrip teks rapat:\n\n{text}"}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Groq summarization failed: {e}")
        return None

# =========================
# OPENAI FALLBACK
# =========================
def summarize_with_openai(text):
    """Meringkas teks menggunakan OpenAI GPT-4o-mini"""
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Anda adalah asisten notulen rapat profesional. "
                        "Buat ringkasan rapat (Notulensi) dalam Bahasa Indonesia yang formal, padat, "
                        "dan mudah dipahami. Tuliskan ringkasan dalam format terstruktur berikut secara singkat:\n\n"
                        "**Poin Penting:**\n(Tuliskan 1-2 poin pembahasan utama rapat secara singkat)\n\n"
                        "**Kesimpulan:**\n(Tuliskan kesimpulan rapat secara singkat)\n\n"
                        "PENTING: Jangan gunakan simbol heading Markdown (seperti ### atau #), jangan gunakan bullet points (seperti - atau *), dan jangan gunakan emoji apa pun di dalam teks Anda. "
                        "Jika ada kesalahan ketik atau salah dengar kecil pada transkrip, perbaiki secara wajar berdasarkan konteks."
                    )
                },
                {"role": "user", "content": f"Berikut adalah transkrip teks rapat:\n\n{text}"}
            ],
            temperature=0.3
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"OpenAI summarization failed: {e}")
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

        # Untuk model T5 Indonesia, kita tambahkan prefix "summarize: " agar model mengenali tugasnya
        t5_input = f"summarize: {text}"

        result = None
        try:
            print("Mencoba model Hugging Face: cahya/t5-base-indonesian-summarization-cased")
            result = client.summarization(
                t5_input,
                model="cahya/t5-base-indonesian-summarization-cased"
            )
        except Exception as e:
            print(f"Model cahya gagal: {e}")

        # Jika gagal dengan model pertama, coba model alternatif Indonesia lainnya
        if not result or (hasattr(result, 'summary_text') and not result.summary_text):
            print("Model pertama gagal, mencoba model alternatif: panggi/t5-base-indonesian-summarization-cased...")
            try:
                result = client.summarization(
                    t5_input,
                    model="panggi/t5-base-indonesian-summarization-cased"
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

    # PRIORITAS 1: Jika GROQ_API_KEY tersedia, gunakan Groq Llama3 untuk kualitas maksimal & cepat
    if GROQ_API_KEY:
        print("Mencoba membuat ringkasan rapat menggunakan Groq API...")
        summary = summarize_with_groq(text)
        if summary:
            return summary
        print("Groq API gagal, mencoba OpenAI/Hugging Face...")

    # PRIORITAS 2: Jika OPENAI_API_KEY tersedia, gunakan OpenAI
    if OPENAI_API_KEY:
        print("Menggunakan OpenAI untuk membuat ringkasan rapat...")
        summary = summarize_with_openai(text)
        if summary:
            return summary
        print("OpenAI gagal, beralih ke model lokal/Hugging Face...")

    # PRIORITAS 3: Fallback ke model lokal/Hugging Face (T5)
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


# =========================
# GENERATE NEWS FOR HUMAS KEMENAG
# =========================
def generate_berita_kemenag(kegiatan, tempat, peserta, content):
    """Mengubah transkrip/ringkasan rapat menjadi draf berita formal Humas Kemenag"""
    # Pastikan data teks tidak kosong
    if not content or content == "-":
        return "Tidak ada isi rapat/transkrip yang bisa diolah menjadi berita."

    # Siapkan prompt untuk AI
    prompt = (
        "Anda adalah staf Hubungan Masyarakat (Humas) Kementerian Agama Kabupaten Jombang yang profesional dan jurnalis senior.\n"
        "Tugas Anda adalah membuat artikel berita formal (Siaran Pers / Press Release) berbahasa Indonesia yang siap dipublikasikan berdasarkan notulensi rapat di bawah ini.\n\n"
        f"INFORMASI KEGIATAN:\n"
        f"- Nama Kegiatan: {kegiatan}\n"
        f"- Tempat: {tempat}\n"
        f"- Peserta: {peserta}\n\n"
        f"Bahan Ringkasan/Notulensi:\n{content}\n\n"
        "KETENTUAN PENULISAN BERITA:\n"
        "1. Tuliskan Judul Berita di baris pertama yang menarik, informatif, dan formal. Jangan gunakan tanda petik ganda untuk membungkus seluruh judul.\n"
        "2. Berita harus diawali dengan dateline formal Kemenag Jombang, yaitu: 'Jombang (Kemenag) -- ' (menggunakan dua tanda strip/minus).\n"
        "3. Paragraf pertama (Lead) harus memuat unsur 5W+1H (Apa kegiatannya, siapa penyelenggara/peserta utamanya, kapan, di mana, dan tujuannya).\n"
        "4. Paragraf berikutnya menjelaskan pembahasan utama, kesepakatan, kutipan pendapat, dan arahan penting dalam rapat secara mengalir dan naratif.\n"
        "5. Gunakan bahasa jurnalistik yang mengalir, resmi, ejaan baku (PUEBI/EYD), dan tidak menggunakan bullet points.\n"
        "6. Akhiri berita dengan tanda penutup inisial Humas seperti '(hms)' atau '(dsi)' di akhir kalimat paragraf terakhir.\n"
        "7. Di baris paling bawah setelah teks berita (tambahkan baris baru kosong pembatas), tuliskan secara presisi teks berikut:\n"
        "Penulis: \n"
        "Editor: \n"
        "(Biarkan setelah kata 'Penulis: ' dan 'Editor: ' kosong tanpa teks apa pun agar bisa diisi secara manual oleh pengguna).\n"
        "8. HANYA kembalikan teks berita utuh saja. Jangan tambahkan kata-kata pengantar seperti 'Berikut adalah berita...', jangan gunakan simbol markdown heading (#, ##, ###) untuk memisahkan bagian berita."
    )

    # PRIORITAS 1: Coba Groq Llama 3.1
    if GROQ_API_KEY:
        try:
            from openai import OpenAI
            groq_client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )

            print("Menghubungi Groq API untuk generate berita Humas Kemenag...")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Anda adalah asisten penulisan berita Humas Kementerian Agama yang profesional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            berita = response.choices[0].message.content.strip()
            if berita:
                return berita
        except Exception as e:
            print(f"Groq news generation failed: {e}")

    # PRIORITAS 2: Coba OpenAI GPT-4o-mini
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            openai_client = OpenAI(api_key=OPENAI_API_KEY)

            print("Menghubungi OpenAI API untuk generate berita Humas Kemenag...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Anda adalah asisten penulisan berita Humas Kementerian Agama yang profesional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            berita = response.choices[0].message.content.strip()
            if berita:
                return berita
        except Exception as e:
            print(f"OpenAI news generation failed: {e}")

    # FALLBACK: Sederhana jika API gagal semua
    return (
        f"Kemenag Jombang Gelar Rapat {kegiatan}\n\n"
        f"Jombang (Kemenag) -- Kantor Kementerian Agama Kabupaten Jombang menggelar kegiatan {kegiatan} bertempat di {tempat}. Rapat ini dihadiri oleh {peserta}.\n\n"
        f"Dalam rapat tersebut, dibahas mengenai beberapa poin penting, yaitu:\n{content}\n\n"
        f"Diharapkan seluruh pihak dapat menindaklanjuti hasil kegiatan ini demi kelancaran tugas bersama. (hms)\n\n"
        f"Penulis: \n"
        f"Editor: "
    )