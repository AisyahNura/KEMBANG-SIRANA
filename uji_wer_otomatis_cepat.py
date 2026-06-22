import os
import time
import torch
import whisper
import jiwer
from dotenv import load_dotenv

# Load environment variables (untuk mengambil GROQ_API_KEY)
load_dotenv()

# =====================================================================
# 1. REFERENSI / NASKAH ASLI (TRUTH)
# =====================================================================
from uji_wer import reference as reference_1
from uji_wer2 import reference as reference_2

# =====================================================================
# 2. DEFINISI ALAT PEMBERSIH TEKS (NORMALISASI)
# =====================================================================
transformasi = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip()
])

# =====================================================================
# 3. FUNGSI TRANSKRIPSI GROQ
# =====================================================================
def transcribe_groq(audio_path):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("   [!] GROQ_API_KEY tidak ditemukan di .env. Groq API dilewati.")
        return None
        
    from services.transkripsi_service import compress_audio_if_needed
    path_to_use, is_temp = compress_audio_if_needed(audio_path)
    
    try:
        from openai import OpenAI
        groq_client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        with open(path_to_use, "rb") as audio_file:
            response = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json",
                language="id",
                temperature=0
            )
        
        if is_temp and os.path.exists(path_to_use):
            try:
                os.remove(path_to_use)
            except Exception:
                pass
                
        if hasattr(response, "model_dump"):
            res_dict = response.model_dump()
        else:
            res_dict = dict(response)
        return res_dict.get("text", "").strip()
    except Exception as e:
        print(f"   [!] Gagal transkripsi Groq: {e}")
        return None

# =====================================================================
# 4. CARI LOKASI FILE AUDIO
# =====================================================================
def cari_audio(pilihan):
    if pilihan == 1:
        paths = ["Audio rapat 1.aac", "uploads/audio/Audio_rapat_1.aac", "uploads/audio/Audio rapat 1.aac"]
    else:
        paths = ["Audio_rapat_2.aac", "uploads/audio/Audio_rapat_2.aac", "uploads/audio/audio_rpaat_22.aac"]
        
    for p in paths:
        if os.path.exists(p):
            return p
    return None

# =====================================================================
# 5. JALANKAN SECARA OTOMATIS TANPA TANYA
# =====================================================================
def main():
    print("==========================================================")
    print("        SISTEM EVALUASI WER OTOMATIS (CEPAT & LENGKAP)    ")
    print("==========================================================")
    print("[Info] Menjalankan transkripsi otomatis untuk Audio 1 dan Audio 2.")
    print("[Info] Model yang diuji: Groq API, Whisper Tiny, Whisper Base, Whisper Small.")

    audios_to_test = [
        (1, "Audio Rapat 1 (12 Menit)", reference_1),
        (2, "Audio Rapat 2 (11 Menit)", reference_2)
    ]

    # Deteksi Akselerasi Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    fp16_available = torch.cuda.is_available()
    print(f"[Info] Akselerasi Hardware: {device.upper()}")
    if device == "cpu":
        print("[!] PERINGATAN: Transkripsi lokal berjalan di CPU.")
        print("[!] Proses ini memakan waktu total sekitar 5-10 menit. Silakan ditunggu.")

    hasil_akhir = {}

    for num, label, ref in audios_to_test:
        audio_path = cari_audio(num)
        if not audio_path:
            print(f"\n[Error] File audio untuk {label} tidak ditemukan!")
            continue

        print(f"\n>>> MEMPROSES: {label} ({audio_path})")
        hasil_audio = []

        ref_bersih = transformasi(ref)

        # A. Groq API
        print("    [1/4] Menjalankan Groq API (Whisper Large-V3)...")
        start = time.time()
        teks_groq = transcribe_groq(audio_path)
        durasi = time.time() - start
        if teks_groq:
            teks_groq_bersih = transformasi(teks_groq)
            wer = jiwer.wer(ref_bersih, teks_groq_bersih)
            hasil_audio.append({
                "model": "Groq API (Large-V3)",
                "durasi": f"{durasi:.1f}s",
                "wer": f"{wer:.4f}",
                "wer_pct": f"{wer * 100:.2f}%"
            })
            print(f"          Selesai! Waktu: {durasi:.1f}s | WER: {wer:.4f} ({wer * 100:.2f}%)")
        else:
            print("          Gagal memproses Groq API.")

        # B. Whisper Tiny
        print("    [2/4] Menjalankan Whisper Tiny (Lokal)...")
        try:
            start = time.time()
            model = whisper.load_model("tiny", device=device)
            result = model.transcribe(audio_path, language="id", fp16=fp16_available)
            teks_tiny = result.get("text", "").strip()
            durasi = time.time() - start
            teks_tiny_bersih = transformasi(teks_tiny)
            wer = jiwer.wer(ref_bersih, teks_tiny_bersih)
            hasil_audio.append({
                "model": "Whisper Tiny (Lokal)",
                "durasi": f"{durasi:.1f}s",
                "wer": f"{wer:.4f}",
                "wer_pct": f"{wer * 100:.2f}%"
            })
            print(f"          Selesai! Waktu: {durasi:.1f}s | WER: {wer:.4f} ({wer * 100:.2f}%)")
        except Exception as e:
            print(f"          Gagal memproses Whisper Tiny: {e}")

        # C. Whisper Base
        print("    [3/4] Menjalankan Whisper Base (Lokal)...")
        try:
            start = time.time()
            model = whisper.load_model("base", device=device)
            result = model.transcribe(audio_path, language="id", fp16=fp16_available)
            teks_base = result.get("text", "").strip()
            durasi = time.time() - start
            teks_base_bersih = transformasi(teks_base)
            wer = jiwer.wer(ref_bersih, teks_base_bersih)
            hasil_audio.append({
                "model": "Whisper Base (Lokal)",
                "durasi": f"{durasi:.1f}s",
                "wer": f"{wer:.4f}",
                "wer_pct": f"{wer * 100:.2f}%"
            })
            print(f"          Selesai! Waktu: {durasi:.1f}s | WER: {wer:.4f} ({wer * 100:.2f}%)")
        except Exception as e:
            print(f"          Gagal memproses Whisper Base: {e}")

        # D. Whisper Small
        print("    [4/4] Menjalankan Whisper Small (Lokal)...")
        try:
            start = time.time()
            model = whisper.load_model("small", device=device)
            result = model.transcribe(audio_path, language="id", fp16=fp16_available)
            teks_small = result.get("text", "").strip()
            durasi = time.time() - start
            teks_small_bersih = transformasi(teks_small)
            wer = jiwer.wer(ref_bersih, teks_small_bersih)
            hasil_audio.append({
                "model": "Whisper Small (Lokal)",
                "durasi": f"{durasi:.1f}s",
                "wer": f"{wer:.4f}",
                "wer_pct": f"{wer * 100:.2f}%"
            })
            print(f"          Selesai! Waktu: {durasi:.1f}s | WER: {wer:.4f} ({wer * 100:.2f}%)")
        except Exception as e:
            print(f"          Gagal memproses Whisper Small: {e}")

        hasil_akhir[label] = hasil_audio

    # Cetak Hasil Akhir Semua Uji Coba
    print("\n==========================================================")
    print("                TABEL PERBANDINGAN WER AKHIR              ")
    print("==========================================================")
    for label, hasil_audio in hasil_akhir.items():
        print(f"\n>>> {label}")
        print(f"----------------------------------------------------------")
        print(f"{'Nama Model / API':<25} | {'Waktu Transkrip':<15} | {'Skor WER':<10} | {'Error (%)':<10}")
        print(f"----------------------------------------------------------")
        for r in hasil_audio:
            print(f"{r['model']:<25} | {r['durasi']:<15} | {r['wer']:<10} | {r['wer_pct']:<10}")
        print(f"----------------------------------------------------------")

if __name__ == "__main__":
    main()
