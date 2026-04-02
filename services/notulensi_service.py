import os

def generate_notulensi(audio_filename, kegiatan, tempat, peserta, transcript, cleaned_text, summary):
    output_folder = "outputs/notulensi"
    os.makedirs(output_folder, exist_ok=True)

    base_name = os.path.splitext(audio_filename)[0]
    txt_filename = base_name + ".txt"
    txt_path = os.path.join(output_folder, txt_filename)

    daftar_peserta = peserta if peserta else "Tidak ada data peserta"

    isi = f"""NOTULENSI RAPAT

Nama Kegiatan : {kegiatan}
Tempat        : {tempat}
Peserta       : {daftar_peserta}
File Rekaman  : {audio_filename}

RINGKASAN
{summary}

HASIL TRANSKRIP BERSIH
{cleaned_text}

TRANSKRIP ASLI
{transcript}
"""

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(isi)

    return txt_path, isi