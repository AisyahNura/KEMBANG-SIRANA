import os
import whisper
import torch
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
model = None

def get_model():
    global model
    if model is None:
        print("Memuat model Whisper...")
        # Deteksi GPU otomatis
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Menggunakan device: {device}")
        model = whisper.load_model("small", device=device)
    return model

def compress_audio_if_needed(file_path):
    """
    Memeriksa apakah ukuran file audio/video lebih besar dari 25MB. 
    Jika iya, kompres menggunakan pydub menjadi mono MP3 32kbps agar dapat diproses oleh OpenAI API.
    """
    max_bytes = 25 * 1024 * 1024  # 25 MB
    
    if not os.path.exists(file_path):
        return file_path, False
        
    file_size = os.path.getsize(file_path)
    if file_size <= max_bytes:
        print(f"Ukuran file: {file_size / 1024 / 1024:.2f} MB (di bawah limit 25MB, tidak perlu kompresi).")
        return file_path, False
        
    print(f"Ukuran file: {file_size / 1024 / 1024:.2f} MB (melebihi limit 25MB OpenAI).")
    print("Memulai kompresi audio ke MP3 mono 32kbps...")
    
    try:
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name_part, _ = os.path.splitext(base_name)
        temp_path = os.path.join(dir_name, f"temp_{name_part}_compressed.mp3")
        
        # Load berkas audio/video menggunakan pydub
        sound = AudioSegment.from_file(file_path)
        
        # Ekspor sebagai mono 32kbps MP3
        sound.export(temp_path, format="mp3", bitrate="32k", parameters=["-ac", "1"])
        
        new_size = os.path.getsize(temp_path)
        print(f"Kompresi selesai. Ukuran file baru: {new_size / 1024 / 1024:.2f} MB")
        
        # Jika masih melebihi 25MB (untuk rekaman yang sangat panjang), turunkan ke 16kbps
        if new_size > max_bytes:
            print("File hasil kompresi masih di atas 25MB, mencoba kompresi ulang ke 16kbps...")
            sound.export(temp_path, format="mp3", bitrate="16k", parameters=["-ac", "1"])
            print(f"Kompresi ulang selesai. Ukuran file akhir: {os.path.getsize(temp_path) / 1024 / 1024:.2f} MB")
            
        return temp_path, True
        
    except Exception as e:
        print(f"Gagal melakukan kompresi audio: {e}")
        # Kembalikan file asli sebagai cadangan terakhir
        return file_path, False

def transcribe_audio_complete(file_path):
    """Transkripsi lengkap: text + segments dalam satu panggilan"""
    # 1. Coba menggunakan Groq Whisper API jika API Key tersedia
    if GROQ_API_KEY:
        print("Menggunakan Groq Whisper API untuk transkripsi cepat...")
        try:
            path_to_use, is_temp = compress_audio_if_needed(file_path)
            
            from openai import OpenAI
            groq_client = OpenAI(
                api_key=GROQ_API_KEY,
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
            
            # Hapus file sementara jika ada
            if is_temp and os.path.exists(path_to_use):
                try:
                    os.remove(path_to_use)
                    print("File kompresi sementara berhasil dihapus.")
                except Exception as ex:
                    print(f"Gagal menghapus file kompresi sementara: {ex}")
            
            # Serialisasi response ke dict agar kompatibel dengan pemrosesan lama
            if hasattr(response, "model_dump"):
                res_dict = response.model_dump()
            else:
                res_dict = dict(response)
                
            return {
                "text": res_dict.get("text", "").strip(),
                "segments": res_dict.get("segments", [])
            }
            
        except Exception as e:
            print("Gagal menggunakan Groq Whisper API, beralih ke alternatif...", e)

    # 2. Coba menggunakan OpenAI Whisper API jika API Key tersedia
    if OPENAI_API_KEY:
        print("Menggunakan OpenAI Whisper API untuk transkripsi cepat...")
        try:
            path_to_use, is_temp = compress_audio_if_needed(file_path)
            
            from openai import OpenAI
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            with open(path_to_use, "rb") as audio_file:
                response = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language="id",
                    temperature=0
                )
            
            # Hapus file sementara jika ada
            if is_temp and os.path.exists(path_to_use):
                try:
                    os.remove(path_to_use)
                    print("File kompresi sementara berhasil dihapus.")
                except Exception as ex:
                    print(f"Gagal menghapus file kompresi sementara: {ex}")
            
            # Serialisasi response ke dict agar kompatibel dengan pemrosesan lama
            if hasattr(response, "model_dump"):
                res_dict = response.model_dump()
            else:
                res_dict = dict(response)
                
            return {
                "text": res_dict.get("text", "").strip(),
                "segments": res_dict.get("segments", [])
            }
            
        except Exception as e:
            print("Gagal menggunakan OpenAI Whisper API, beralih ke model lokal Whisper:", e)

    # 2. Fallback / Cadangan menggunakan model Whisper lokal
    try:
        model = get_model()
        fp16_available = torch.cuda.is_available()
        print(f"GPU acceleration: {'Enabled' if fp16_available else 'Disabled'}")

        result = model.transcribe(
            file_path,
            language="id",
            fp16=fp16_available,
            temperature=0,
            verbose=True
        )

        return {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", [])
        }

    except Exception as e:
        print("ERROR TRANSKRIP COMPLETE:", e)
        return {"text": "", "segments": []}

def transcribe_audio(file_path):
    res = transcribe_audio_complete(file_path)
    return res.get("text", "")

def transcribe_audio_with_segments(file_path):
    res = transcribe_audio_complete(file_path)
    return res.get("segments", [])