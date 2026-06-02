from jiwer import wer

# =========================
# REFERENCE / TRANSKRIP ASLI
# =========================
reference = """
ada pertemuan hari ini dibahas pentingnya peningkatan kualitas pembelajaran di sekolah.
Guru diharapkan dapat menggunakan metode pembelajaran yang lebih interaktif agar siswa lebih aktif dalam proses belajar.
Selain itu, penggunaan teknologi seperti media digital juga dianjurkan untuk membantu pemahaman materi.
Di akhir diskusi, disepakati bahwa setiap guru akan mencoba menerapkan metode pembelajaran baru secara bertahap mulai semester depan.
"""

# =========================
# MODEL TINY
# =========================
tiny = """
Pada bertemuan hari ini, dipahas pentingnya peningkatan kualitas pembelajaran diskola.
Kuru diariakan dapat menggunakan metodepembelajaran yang lebih interactive, akarsisual lebih aktif dalam proses pleasure.
Selain itu, penggunaan teknologi seperti media digital yang dianjurkan untuk membantu mengenmal materi,
di akhir diskusi, dispakati bahwa setiap kuru akan menerapkan metodepembelajaran baru secara berataha mulai semesterdepan.
Kau bisa menenum, menenum, menenum, menenum, menenum, menenum, menenum, menenum, menenum, menenum, menenum, menenum.
"""

# =========================
# MODEL BASE
# =========================
base = """
Pada bertemu aneh hari ini di bahas pentingnya peningkatan kualitas pembelajaran di sekolah.
Guru diharapkan dapat menggunakan metode pembelajaran yang lebih interaktif, akan sisual lebih aktif dalam proses pelajar.
Selain itu, penggunaan teknologi seperti media digital yang dihancurkan untuk membantu berman-manan materi di akhir diskusi,
di spakati bahwa setiap guru akan mencupa menerapkan metode pembelajaran baru secara perlatahan mulai semasar depan.
"""

# =========================
# MODEL SMALL
# =========================
small = """
Pada bertemuan hari ini dibahas pentingnya peningkatan kualitas pembelajaran di sekolah.
Guru diharapkan dapat menggunakan metode pembelajaran yang lebih interaktif agar sisoa lebih aktif dalam proses belajar.
Selain itu, penggunaan teknologi seperti medier digital yang dianjurkan untuk membantu pemahaman materi,
di akhir diskusi, disepakati bahwa setiap guru akan mencoba menerapkan metode pembelajaran baru secara bertahap mulai semester depan.
"""

# =========================
# HITUNG WER
# =========================
wer_tiny = wer(reference, tiny)
wer_base = wer(reference, base)
wer_small = wer(reference, small)

# =========================
# HASIL
# =========================
print("=== HASIL WER ===")
print(f"Tiny  : {wer_tiny:.3f}")
print(f"Base  : {wer_base:.3f}")
print(f"Small : {wer_small:.3f}")