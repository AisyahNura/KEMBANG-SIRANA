import os

OUTPUT_FOLDER = "outputs/notulensi"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def generate_notulensi(
    filename,
    kegiatan,
    tempat,
    peserta,
    diarization_text="",
    transkrip_asli="",
    transkrip_bersih="",
    ringkasan="",
    jenis_proses="transkrip"
):
    peserta_text = peserta if peserta else "-"

    if jenis_proses == "transkrip":
        judul_hasil = "HASIL TRANSKRIPSI"
        isi_hasil = transkrip_bersih.strip() if transkrip_bersih else "-"
    elif jenis_proses == "summary":
        judul_hasil = "HASIL RINGKASAN"
        isi_hasil = ringkasan.strip() if ringkasan else "-"
    elif jenis_proses == "diarization":
        judul_hasil = "HASIL DIARIZATION"
        isi_hasil = diarization_text.strip() if diarization_text else "Diarization tidak berhasil diproses."
    else:
        judul_hasil = "HASIL"
        isi_hasil = "-"

    isi_notulensi = f"""NOTULENSI RAPAT

Nama Kegiatan : {kegiatan}
Tempat        : {tempat}
Peserta       : {peserta_text}
File Rekaman  : {filename}
Jenis Proses  : {jenis_proses.upper()}

{judul_hasil}
{isi_hasil}
"""

    nama_file = f"notulensi_{jenis_proses}_{os.path.splitext(filename)[0]}.txt"
    file_path = os.path.join(OUTPUT_FOLDER, nama_file)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(isi_notulensi)

    return file_path, isi_notulensi