import os
import warnings
import torch
import torchaudio
from dotenv import load_dotenv
from pydub import AudioSegment

# Suppress the torchcodec warning when pyannote tries to probe built-in decoding.
# We still support diarization by providing in-memory waveform data.
warnings.filterwarnings(
    "ignore",
    message=r"torchcodec is not installed correctly so built-in audio decoding will fail.*",
    category=UserWarning,
    module=r"pyannote\.audio\..*"
)

from pyannote.audio import Pipeline

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
pipeline = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Kalau ffmpeg belum otomatis kebaca, aktifkan ini:
# AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
# AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
# AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

def load_diarization_pipeline():
    global pipeline

    if pipeline is not None:
        return pipeline

    if not HF_TOKEN:
        raise Exception("HF_TOKEN tidak ditemukan di file .env")

    try:
        print("Memuat model diarization...")
        pipeline_local = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN
        )

        if hasattr(pipeline_local, "to"):
            pipeline_local.to(DEVICE)

        pipeline = pipeline_local
        print(f"Model diarization berhasil dimuat di {DEVICE}")
        return pipeline

    except Exception as e:
        raise Exception(f"Gagal memuat model diarization: {str(e)}")

def convert_audio_for_diarization(input_path):
    try:
        if not os.path.exists(input_path):
            raise Exception("File audio tidak ditemukan")

        output_path = os.path.splitext(input_path)[0] + "_diarization.wav"

        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio.export(output_path, format="wav")

        return output_path

    except Exception as e:
        raise Exception(f"Gagal convert audio untuk diarization: {str(e)}")

def load_audio_to_memory(wav_path):
    try:
        waveform, sample_rate = torchaudio.load(wav_path)

        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=16000
            )
            waveform = resampler(waveform)
            sample_rate = 16000

        return {
            "waveform": waveform,
            "sample_rate": sample_rate
        }

    except Exception as e:
        raise Exception(f"Gagal load audio ke memory: {str(e)}")

def format_seconds(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def merge_segments(segments, gap_threshold=1.5):
    if not segments:
        return []

    merged = [segments[0]]

    for current in segments[1:]:
        last = merged[-1]

        same_speaker = current["speaker"] == last["speaker"]
        close_gap = (current["start"] - last["end"]) <= gap_threshold

        if same_speaker and close_gap:
            last["end"] = current["end"]
            last["end_str"] = format_seconds(current["end"])
        else:
            merged.append(current)

    return merged

def diarize_audio(file_path):
    try:
        model = load_diarization_pipeline()
        wav_path = convert_audio_for_diarization(file_path)
        audio_data = load_audio_to_memory(wav_path)

        print("Memulai proses diarization...")

        with torch.inference_mode():
            print("Memulai proses diarization...")
            diarization_output = model(audio_data)
            print("Diarization selesai diproses")

        if hasattr(diarization_output, "itertracks"):
            diarization_annotation = diarization_output
        elif hasattr(diarization_output, "speaker_diarization"):
            diarization_annotation = diarization_output.speaker_diarization
        else:
            raise Exception(f"Format output diarization tidak dikenali: {type(diarization_output)}")

        segments = []
        speaker_map = {}
        speaker_count = 1

        for turn, _, speaker in diarization_annotation.itertracks(yield_label=True):
            if speaker not in speaker_map:
                speaker_map[speaker] = f"Speaker {speaker_count}"
                speaker_count += 1

            start_time = round(turn.start, 2)
            end_time = round(turn.end, 2)

            if end_time <= start_time:
                continue

            durasi = end_time - start_time
            if durasi < 0.5:
                continue

            segments.append({
                "speaker": speaker_map[speaker],
                "start": start_time,
                "end": end_time,
                "start_str": format_seconds(start_time),
                "end_str": format_seconds(end_time)
            })

        if not segments:
            return {
                "success": False,
                "segments": [],
                "text": "Tidak ada speaker yang terdeteksi.",
                "error": None
            }

        segments = merge_segments(segments)

        diarization_lines = []
        for seg in segments:
            diarization_lines.append(
                f"[{seg['start_str']} - {seg['end_str']}] {seg['speaker']}"
            )

        diarization_text = "\n".join(diarization_lines)

        return {
            "success": True,
            "segments": segments,
            "text": diarization_text,
            "error": None
        }

    except Exception as e:
        print("ERROR DIARIZATION SERVICE:", e)
        return {
            "success": False,
            "segments": [],
            "text": "Diarization tidak berhasil diproses.",
            "error": str(e)
        }

def assign_speakers_to_transcript(diarization_segments, transcript_segments):
    hasil = []

    for t in transcript_segments:
        t_start = float(t.get("start", 0))
        t_end = float(t.get("end", 0))
        t_text = t.get("text", "").strip()

        if not t_text:
            continue

        best_speaker = "Speaker Tidak Diketahui"
        best_overlap = 0

        for d in diarization_segments:
            d_start = float(d["start"])
            d_end = float(d["end"])

            overlap = max(0, min(t_end, d_end) - max(t_start, d_start))

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = d["speaker"]

        hasil.append({
            "speaker": best_speaker,
            "start": t_start,
            "end": t_end,
            "text": t_text
        })

    return hasil

def format_speaker_transcript(speaker_transcript):
    if not speaker_transcript:
        return "Tidak ada hasil speaker."

    merged = []

    for item in speaker_transcript:
        if not merged:
            merged.append(item)
            continue

        last = merged[-1]

        same_speaker = last["speaker"] == item["speaker"]
        close_gap = (item["start"] - last["end"]) <= 1.5

        if same_speaker and close_gap:
            last["end"] = item["end"]
            last["text"] += " " + item["text"]
        else:
            merged.append(item)

    lines = []
    for item in merged:
        lines.append(
            f"[{format_seconds(item['start'])} - {format_seconds(item['end'])}] {item['speaker']}\n{item['text']}"
        )

    return "\n\n".join(lines)