import whisper
import torch

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

def transcribe_audio(file_path):
    try:
        model = get_model()
        # Aktifkan GPU acceleration jika tersedia
        fp16_available = torch.cuda.is_available()
        print(f"GPU acceleration: {'Enabled' if fp16_available else 'Disabled'}")

        def progress_callback(progress):
            print(f"Progress transkripsi: {progress:.1f}%")

        result = model.transcribe(
            file_path,
            language="id",
            fp16=fp16_available,  # Auto-detect GPU
            temperature=0,
            verbose=True  # Show progress
        )
        return result.get("text", "").strip()
    except Exception as e:
        print("ERROR TRANSKRIP SERVICE:", e)
        return ""

def transcribe_audio_with_segments(file_path):
    try:
        model = get_model()
        result = model.transcribe(
            file_path,
            language="id",
            fp16=False,
            temperature=0
        )
        return result.get("segments", [])
    except Exception as e:
        print("ERROR TRANSKRIP SEGMENT:", e)
        return []

def transcribe_audio_complete(file_path):
    """Transkripsi lengkap: text + segments dalam satu panggilan"""
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

        # Kembalikan kedua hasil sekaligus
        return {
            "text": result.get("text", "").strip(),
            "segments": result.get("segments", [])
        }

    except Exception as e:
        print("ERROR TRANSKRIP COMPLETE:", e)
        return {"text": "", "segments": []}