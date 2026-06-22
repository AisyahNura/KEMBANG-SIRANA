import jiwer

# =====================================================================
# 1. TEKS ACUAN / REFERENCE (Naskah Asli yang Anda Baca saat Perekaman)
# =====================================================================
reference = """
Selamat pagi dan salam sejahtera bagi kita semua.

Marilah kita panjatkan puji dan syukur ke hadirat Tuhan Yang Maha Esa karena atas rahmat dan karunia-Nya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat. Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah hadir dan meluangkan waktu untuk mengikuti rapat ini.

Pada kesempatan kali ini, kita akan membahas mengenai peningkatan kualitas pelayanan di lingkungan Kementerian Agama. Sebagai instansi yang memiliki peran penting dalam memberikan pelayanan kepada masyarakat, Kementerian Agama dituntut untuk terus meningkatkan kualitas kerja agar pelayanan yang diberikan dapat berjalan dengan baik, cepat, dan sesuai dengan kebutuhan masyarakat.

Dalam pelaksanaan tugas sehari-hari, pelayanan yang baik tidak hanya ditentukan oleh kemampuan individu, tetapi juga oleh kerja sama dan koordinasi yang baik antarpegawai maupun antarbagian. Oleh karena itu, setiap pegawai diharapkan dapat menjalankan tugas dan tanggung jawabnya dengan penuh disiplin serta menjaga komunikasi yang baik dengan rekan kerja. Dengan adanya koordinasi yang baik, setiap informasi dapat tersampaikan secara jelas sehingga pekerjaan dapat diselesaikan dengan lebih efektif dan efisien.

Selain itu, ketepatan waktu juga menjadi salah satu faktor penting dalam memberikan pelayanan yang berkualitas. Setiap pekerjaan yang diberikan hendaknya dapat diselesaikan sesuai dengan jadwal yang telah ditentukan. Dengan demikian, berbagai layanan yang dibutuhkan masyarakat dapat diberikan tanpa mengalami keterlambatan. Sikap disiplin dan tanggung jawab dalam bekerja merupakan bagian penting yang harus terus ditingkatkan oleh seluruh pegawai.

Di era digital seperti saat ini, pemanfaatan teknologi informasi juga menjadi salah satu upaya untuk meningkatkan kualitas pelayanan. Berbagai sistem dan aplikasi yang telah tersedia perlu dimanfaatkan secara maksimal untuk mendukung pengelolaan data, penyampaian informasi, serta administrasi pelayanan. Dengan penggunaan teknologi yang tepat, proses kerja dapat menjadi lebih cepat, akurat, dan transparan sehingga masyarakat dapat merasakan manfaatnya secara langsung.

Kita juga perlu menjaga sikap profesional dalam menjalankan tugas. Profesionalisme tidak hanya terlihat dari kemampuan bekerja, tetapi juga dari sikap yang jujur, sopan, bertanggung jawab, dan berorientasi pada pelayanan. Dengan menerapkan nilai-nilai tersebut, kepercayaan masyarakat terhadap Kementerian Agama dapat terus meningkat dan kualitas pelayanan yang diberikan akan semakin baik.

Melalui rapat ini, saya berharap kita semua dapat bersama-sama berkomitmen untuk meningkatkan kualitas pelayanan di lingkungan Kementerian Agama. Dengan kerja sama yang baik, komunikasi yang efektif, serta semangat untuk terus memperbaiki diri, kita dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik.

Demikian yang dapat saya sampaikan. Terima kasih atas perhatian dan kerja sama seluruh peserta rapat. Semoga hasil rapat hari ini dapat memberikan manfaat bagi peningkatan kualitas pelayanan dan kinerja kita bersama.

Selamat pagi
"""

# =====================================================================
# 2. TEKS HASIL TRANSKRIPSI (Salin hasil dari website ke sini)
# =====================================================================
# Tempelkan hasil transkripsi dari website ke dalam masing-masing variabel di bawah ini:

groq_api = """
Selamat pagi dan salam sejahtera bagi kita semua marilah kita panjatkan puji dan syukur kehadirat Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah hadir dan meluangkan waktu untuk mengikuti rapat ini Pada kesempatan kali ini, kita akan membahas mengenai peningkatan kualitas pelayanan di lingkungan Kementerian Agama Sebagai instasi yang memiliki peran penting dalam memberikan pelayanan kepada masyarakat kementerian agama dituntut untuk terus meningkatkan kualitas kerja agar pelayanan yang diberikan dapat berjalan dengan baik, cepat, dan sesuai dengan kebutuhan Dalam pelaksanaan tugas sehari-hari pelayanan yang baik tidak hanya ditentukan oleh kemampuan individu tetapi juga oleh kerja sama dan koordinasi yang baik antar pegawai maupun antar bagian Oleh karena itu, setiap pegawai diharapkan dapat menjalankan tugas dan tanggung jawabnya dengan penuh disiplin serta menjaga komunikasi yang baik dengan rekan kerja Dengan adanya koordinasi yang baik, setiap informasi dapat tersampaikan secara jelas sehingga pekerjaan dapat diselesaikan dengan lebih efektif dan efisien Selain itu, ketepatan waktu juga menjadi salah satu faktor penting dalam memberikan pelayanan yang berkualitas Setiap pekerjaan yang diberikan hendaknya dapat diselesaikan sesuai dengan jadwal yang telah ditentukan Dengan demikian berbagai layanan yang dibutuhkan masyarakat dapat diberikan tanpa mengalami keterlambatan Sikap disiplin dan tanggung jawab dalam bekerja merupakan bagian penting yang harus terus ditingkatkan oleh seluruh pegawai. Di era digital seperti ini pemanfaatan teknologi informasi juga menjadi salah satu upaya untuk meningkatkan kualitas pelayanan berbagai sistem dan aplikasi yang telah tersedia perlu dimanfaatkan secara maksimal untuk mendukung pengelolaan data penyampaian informasi serta administrasi pelayanan dengan penggunaan teknologi yang tepat proses kerja dapat menjadi lebih cepat akurat dan transparan sehingga masyarakat dapat merasakan manfaatnya secara langsung kita juga perlu menjaga sikap profesional dalam menjalankan tugas Profesionalisme tidak hanya terlihat dari kemampuan pekerja tetapi juga dari sikap yang jujur, sopan bertanggung jawab dan berorientasi pada pelayanan dengan menerapkan nilai-nilai tersebut kepercayaan masyarakat terhadap kementerian agama dapat terus meningkat dan kualitas pelayanan yang diberikan akan semakin baik. Melalui rapat ini, saya berharap kita semua dapat bersama-sama berkomitmen untuk meningkatkan kualitas pelayanan di lingkungan Kementerian Agama. Dengan kerja sama yang baik, komunikasi yang efektif, serta semangat untuk terus memperbaiki diri, kita dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik. Demikian yang dapat saya sampaikan, terima kasih atas perhatian dan kerja sama seluruh peserta rapat. Semoga hasil rapat hari ini dapat memberikan manfaat bagi peningkatan kualitas pelayanan dan kinerja kita bersama.
"""
small = """
Selamat pagi dan salam sejahtera bagi kita semua marilah kita panjatkan puji dan syukur kehadirat Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah hadir dan meluangkan waktu untuk mengikuti rapat ini Pada kesempatan kali ini, kita akan membahas mengenai peningkatan kualitas pelayanan di lingkungan Kementerian Agama Sebagai instasi yang memiliki peran penting dalam memberikan pelayanan kepada masyarakat kementerian agama dituntut untuk terus meningkatkan kualitas kerja agar pelayanan yang diberikan dapat berjalan dengan baik, cepat, dan sesuai dengan kebutuhan Dalam pelaksanaan tugas sehari-hari pelayanan yang baik tidak hanya ditentukan oleh kemampuan individu tetapi juga oleh kerja sama dan koordinasi yang baik antar pegawai maupun antar bagian Oleh karena itu, setiap pegawai diharapkan dapat menjalankan tugas dan tanggung jawabnya dengan penuh disiplin serta menjaga komunikasi yang baik dengan rekan kerja Dengan adanya koordinasi yang baik, setiap informasi dapat tersampaikan secara jelas sehingga pekerjaan dapat diselesaikan dengan lebih efektif dan efisien Selain itu, ketepatan waktu juga menjadi salah satu faktor penting dalam memberikan pelayanan yang berkualitas Setiap pekerjaan yang diberikan hendaknya dapat diselesaikan sesuai dengan jadwal yang telah ditentukan Dengan demikian berbagai layanan yang dibutuhkan masyarakat dapat diberikan tanpa mengalami keterlambatan Sikap disiplin dan tanggung jawab dalam bekerja merupakan bagian penting yang harus terus ditingkatkan oleh seluruh pegawai. Di era digital seperti ini pemanfaatan teknologi informasi juga menjadi salah satu upaya untuk meningkatkan kualitas pelayanan berbagai sistem dan aplikasi yang telah tersedia perlu dimanfaatkan secara maksimal untuk mendukung pengelolaan data penyampaian informasi serta administrasi pelayanan dengan penggunaan teknologi yang tepat proses kerja dapat menjadi lebih cepat akurat dan transparan sehingga masyarakat dapat merasakan manfaatnya secara langsung kita juga perlu menjaga sikap profesional dalam menjalankan tugas Profesionalisme tidak hanya terlihat dari kemampuan pekerja tetapi juga dari sikap yang jujur, sopan bertanggung jawab dan berorientasi pada pelayanan dengan menerapkan nilai-nilai tersebut kepercayaan masyarakat terhadap kementerian agama dapat terus meningkat dan kualitas pelayanan yang diberikan akan semakin baik. Melalui rapat ini, saya berharap kita semua dapat bersama-sama berkomitmen untuk meningkatkan kualitas pelayanan di lingkungan Kementerian Agama. Dengan kerja sama yang baik, komunikasi yang efektif, serta semangat untuk terus memperbaiki diri, kita dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik. Demikian yang dapat saya sampaikan, terima kasih atas perhatian dan kerja sama seluruh peserta rapat. Semoga hasil rapat hari ini dapat memberikan manfaat bagi peningkatan kualitas pelayanan dan kinerja kita bersama.
"""
base = """
Selamat pagi dan salam sejahtera bagi kita semua marilah kita panjatkan puji dan syukur kehadirat Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah hadir dan meluangkan waktu untuk mengikuti rapat ini Pada kesempatan kali ini, kita akan membahas mengenai peningkatan kualitas pelayanan di lingkungan Kementerian Agama Sebagai instasi yang memiliki peran penting dalam memberikan pelayanan kepada masyarakat kementerian agama dituntut untuk terus meningkatkan kualitas kerja agar pelayanan yang diberikan dapat berjalan dengan baik, cepat, dan sesuai dengan kebutuhan Dalam pelaksanaan tugas sehari-hari pelayanan yang baik tidak hanya ditentukan oleh kemampuan individu tetapi juga oleh kerja sama dan koordinasi yang baik antar pegawai maupun antar bagian Oleh karena itu, setiap pegawai diharapkan dapat menjalankan tugas dan tanggung jawabnya dengan penuh disiplin serta menjaga komunikasi yang baik dengan rekan kerja Dengan adanya koordinasi yang baik, setiap informasi dapat tersampaikan secara jelas sehingga pekerjaan dapat diselesaikan dengan lebih efektif dan efisien Selain itu, ketepatan waktu juga menjadi salah satu faktor penting dalam memberikan pelayanan yang berkualitas Setiap pekerjaan yang diberikan hendaknya dapat diselesaikan sesuai dengan jadwal yang telah ditentukan Dengan demikian berbagai layanan yang dibutuhkan masyarakat dapat diberikan tanpa mengalami keterlambatan Sikap disiplin dan tanggung jawab dalam bekerja merupakan bagian penting yang harus terus ditingkatkan oleh seluruh pegawai. Di era digital seperti ini pemanfaatan teknologi informasi juga menjadi salah satu upaya untuk meningkatkan kualitas pelayanan berbagai sistem dan aplikasi yang telah tersedia perlu dimanfaatkan secara maksimal untuk mendukung pengelolaan data penyampaian informasi serta administrasi pelayanan dengan penggunaan teknologi yang tepat proses kerja dapat menjadi lebih cepat akurat dan transparan sehingga masyarakat dapat merasakan manfaatnya secara langsung kita juga perlu menjaga sikap profesional dalam menjalankan tugas Profesionalisme tidak hanya terlihat dari kemampuan pekerja tetapi juga dari sikap yang jujur, sopan bertanggung jawab dan berorientasi pada pelayanan dengan menerapkan nilai-nilai tersebut kepercayaan masyarakat terhadap kementerian agama dapat terus meningkat dan kualitas pelayanan yang diberikan akan semakin baik. Melalui rapat ini, saya berharap kita semua dapat bersama-sama berkomitmen untuk meningkatkan kualitas pelayanan di lingkungan Kementerian Agama. Dengan kerja sama yang baik, komunikasi yang efektif, serta semangat untuk terus memperbaiki diri, kita dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik. Demikian yang dapat saya sampaikan, terima kasih atas perhatian dan kerja sama seluruh peserta rapat. Semoga hasil rapat hari ini dapat memberikan manfaat bagi peningkatan kualitas pelayanan dan kinerja kita bersama.
"""

tiny = """
selamat pagi dan salam sejahtera bagi kita semua marilah kita panjatkan puji dan syukur kehadirat Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah hadir dan meluangkan waktu untuk mengikuti rapat ini Pada kesempatan kali ini, kita akan membahas mengenai peningkatan kualitas pelayanan di lingkungan Kementerian Agama Sebagai instasi yang memiliki peran penting dalam memberikan pelayanan kepada masyarakat kementerian agama dituntut untuk terus meningkatkan kualitas kerja agar pelayanan yang diberikan dapat berjalan dengan baik, cepat, dan sesuai dengan kebutuhan Dalam pelaksanaan tugas sehari-hari pelayanan yang baik tidak hanya ditentukan oleh kemampuan individu tetapi juga oleh kerjasama dan koordinasi yang baik antar pegawai maupun antar bagian Oleh karena itu, setiap pegawai diharapkan dapat menjalankan tugas dan tanggung jawabnya dengan penuh disiplin serta menjaga komunikasi yang baik dengan rekan kerja Dengan adanya koordinasi yang baik, setiap informasi dapat tersampaikan secara jelas sehingga pekerjaan dapat diselesaikan dengan lebih efektif dan efisien Selain itu, ketepatan waktu juga menjadi salah satu faktor penting dalam memberikan pelayanan yang berkualitas Setiap pekerjaan yang diberikan hendaknya dapat diselesaikan sesuai dengan jadwal yang telah ditentukan Dengan demikian berbagai layanan yang dibutuhkan masyarakat dapat diberikan tanpa mengalami keterlambatan Sikap disiplin dan tanggung jawab dalam bekerja merupakan bagian penting yang harus terus ditingkatkan oleh seluruh pegawai. di era digital seperti ini pemanfaatan teknologi informasi juga menjadi salah satu upaya untuk meningkatkan kualitas pelayanan berbagai sistem dan aplikasi yang telah tersedia perlu dimanfaatkan secara maksimal untuk mendukung pengelolaan data penyampaian informasi serta administrasi pelayanan dengan penggunaan teknologi yang tepat proses kerja dapat menjadi lebih cepat akurat dan transparan sehingga masyarakat dapat merasakan manfaatnya secara langsung kita juga perlu menjaga sikap profesional dalam menjalankan tugas Profesionalisme tidak hanya terlihat dari kemampuan pekerja tetapi juga dari sikap yang jujur, sopan bertanggung jawab dan berorientasi pada pelayanan dengan menerapkan nilai-nilai tersebut kepercayaan masyarakat terhadap kementerian agama dapat terus meningkat dan kualitas pelayanan yang diberikan akan semakin baik. Melalui rapat ini, saya berharap kita semua dapat bersama-sama berkomitmen untuk meningkatkan kualitas pelayanan di lingkungan Kementerian Agama. Dengan kerjasama yang baik, komunikasi yang efektif, serta semangat untuk terus memperbaiki diri, kita dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik. Demikian yang dapat saya sampaikan, terima kasih atas perhatian dan kerjasama seluruh peserta rapat. Semoga hasil rapat hari ini dapat memberikan manfaat bagi peningkatan kualitas pelayanan dan kinerja kita bersama. Selamat pagi! Terima kasih.
"""

# =====================================================================
# 3. ALAT PEMBERSIH TEKS (NORMALISASI) AGAR HASIL WER ADIL
# =====================================================================
transformasi = jiwer.Compose([
    jiwer.ToLowerCase(),            # Mengubah huruf menjadi kecil semua
    jiwer.RemovePunctuation(),      # Menghapus tanda baca
    jiwer.RemoveMultipleSpaces(),   # Merapikan spasi ganda
    jiwer.Strip()                   # Menghapus spasi di ujung kalimat
])

# =====================================================================
# 4. PROSES HITUNG WER
# =====================================================================
# PENTING: Pustaka jiwer.wer() di bawah ini secara otomatis menggunakan rumus 
# yang sesuai dengan proposal Anda: 
# WER = (S + D + I) / W * 100%
# Di mana:
# - S = Substitutions (jumlah kata yang salah/diganti)
# - D = Deletions (jumlah kata yang hilang/terhapus)
# - I = Insertions (jumlah kata tambahan)
# - W = Jumlah total kata dalam teks acuan (reference)
#
print("=================== HASIL UJI WER MANUAL ===================")

# Bersihkan teks acuan terlebih dahulu
ref_bersih = transformasi(reference)

# Hitung untuk Groq API
if groq_api.strip() and "Masukkan teks" not in groq_api:
    groq_bersih = transformasi(groq_api)
    wer_groq = jiwer.wer(ref_bersih, groq_bersih)
    print(f"Groq API (Large-V3) : {wer_groq:.4f} ({wer_groq * 100:.2f}% Error)")
else:
    print("Groq API (Large-V3) : [Belum diisi]")

# Hitung untuk Whisper Small
if small.strip() and "Masukkan teks" not in small:
    small_bersih = transformasi(small)
    wer_small = jiwer.wer(ref_bersih, small_bersih)
    print(f"Whisper Small (Lokal): {wer_small:.4f} ({wer_small * 100:.2f}% Error)")
else:
    print("Whisper Small (Lokal): [Belum diisi]")

# Hitung untuk Whisper Base
if base.strip() and "Masukkan teks" not in base:
    base_bersih = transformasi(base)
    wer_base = jiwer.wer(ref_bersih, base_bersih)
    print(f"Whisper Base (Lokal) : {wer_base:.4f} ({wer_base * 100:.2f}% Error)")
else:
    print("Whisper Base (Lokal) : [Belum diisi]")

# Hitung untuk Whisper Tiny
if tiny.strip() and "Masukkan teks" not in tiny:
    tiny_bersih = transformasi(tiny)
    wer_tiny = jiwer.wer(ref_bersih, tiny_bersih)
    print(f"Whisper Tiny (Lokal) : {wer_tiny:.4f} ({wer_tiny * 100:.2f}% Error)")
else:
    print("Whisper Tiny (Lokal) : [Belum diisi]")

print("============================================================")