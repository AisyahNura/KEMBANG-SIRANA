import jiwer

# =====================================================================
# 1. TEKS ACUAN / REFERENCE (Naskah Asli yang Anda Baca saat Perekaman)
# =====================================================================
reference = """
Assalamu’alaikum warahmatullahi wabarakatuh.

Selamat pagi dan salam sejahtera untuk kita semua.

Pertama-tama, marilah kita panjatkan puji dan syukur ke hadirat Tuhan Yang Maha Esa karena atas rahmat dan karunia-Nya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat. Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah meluangkan waktu untuk hadir dan berpartisipasi dalam rapat ini.

Pada kesempatan kali ini, kita akan membahas satu topik utama, yaitu peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan. Topik ini sangat penting karena koordinasi yang baik merupakan salah satu faktor utama yang menentukan keberhasilan suatu kegiatan maupun pencapaian target organisasi. Tanpa adanya komunikasi yang efektif dan kerja sama yang baik, berbagai tugas yang telah direncanakan dapat mengalami hambatan dalam pelaksanaannya.

Berdasarkan hasil evaluasi beberapa kegiatan yang telah dilaksanakan sebelumnya, dapat diketahui bahwa sebagian besar program kerja telah berjalan sesuai dengan rencana. Namun, masih terdapat beberapa kendala yang berkaitan dengan proses koordinasi antarbagian. Misalnya, informasi yang terlambat disampaikan, kurangnya pembaruan terkait perkembangan pekerjaan, serta adanya perbedaan pemahaman mengenai tugas dan tanggung jawab masing-masing. Hal-hal tersebut meskipun terlihat sederhana, dapat memengaruhi efektivitas pelaksanaan kegiatan secara keseluruhan.

Oleh karena itu, diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam lingkungan kerja. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan sebaiknya disampaikan secara jelas, tepat, dan tepat waktu kepada pihak yang berkepentingan. Selain itu, setiap bagian juga diharapkan dapat memberikan laporan perkembangan pekerjaan secara berkala sehingga setiap kendala yang muncul dapat segera diketahui dan dicari solusinya bersama.

Koordinasi yang baik tidak hanya berarti menyampaikan informasi, tetapi juga mencakup kemampuan untuk bekerja sama, saling mendukung, dan menghargai peran masing-masing anggota tim. Dengan adanya sikap saling terbuka dan saling membantu, proses kerja akan menjadi lebih lancar dan tujuan yang telah ditetapkan dapat dicapai dengan lebih mudah. Kerja sama yang baik juga dapat mengurangi kesalahan komunikasi yang sering menjadi penyebab terjadinya keterlambatan atau hambatan dalam pekerjaan.

Selain itu, pemanfaatan teknologi juga dapat menjadi salah satu sarana untuk meningkatkan koordinasi. Berbagai platform komunikasi dan sistem digital yang tersedia saat ini dapat digunakan untuk mempermudah penyampaian informasi, pemantauan progres pekerjaan, serta dokumentasi kegiatan. Dengan memanfaatkan teknologi secara optimal, proses komunikasi dapat berlangsung lebih cepat dan efisien sehingga pekerjaan dapat diselesaikan dengan lebih baik.

Saya berharap melalui pembahasan pada rapat hari ini, kita semua dapat semakin menyadari pentingnya koordinasi dan komunikasi dalam mendukung keberhasilan pekerjaan. Marilah kita bersama-sama meningkatkan kerja sama, memperkuat komunikasi, dan membangun lingkungan kerja yang lebih produktif agar setiap target yang telah ditetapkan dapat tercapai secara maksimal.

Demikian yang dapat saya sampaikan. Terima kasih atas perhatian dan kerja sama dari seluruh peserta rapat. Semoga hasil diskusi pada hari ini dapat memberikan manfaat bagi peningkatan kinerja kita bersama.
Wassalamu’alaikum warahmatullahi wabarakatuh
"""

# =====================================================================
# 2. TEKS HASIL TRANSKRIPSI (Salin hasil dari website ke sini)
# =====================================================================
# Tempelkan hasil transkripsi dari website ke dalam masing-masing variabel di bawah ini:

groq_api = """
Assalamualaikum warahmatullahi wabarakatuh Selamat pagi dan salam sejahtera untuk kita semua Pertama-tama, marilah kita panjatkan puji dan syukur kehadiran Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah meluangkan waktu untuk hadir dan berpartisipasi dalam rapat ini Pada kesempatan kali ini, kita akan membahas satu topik utama, yaitu peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan Topik ini sangat penting karena koordinasi yang baik merupakan salah satu faktor utama yang menentukan keberhasilan suatu kegiatan maupun pencapaian target organisasi. Tanpa adanya komunikasi yang efektif dan kerja sama yang baik berbagai tugas yang telah direncanakan dapat mengalami hambatan dalam pelaksanaannya Berdasarkan hasil evaluasi beberapa kegiatan yang telah dilaksanakan sebelumnya, dapat diketahui bahwa sebagian besar program kerja telah berjalan sesuai dengan rencana. Namun, masih terdapat beberapa kendala yang berkaitan dengan proses koordinasi antarabagian Misalnya, pembaruan terkait perkembangan pekerjaan Serta adanya perbedaan pemahaman mengenai tugas dan tanggung jawab masing-masing Hal-hal tersebut meskipun terlihat sederhana dapat memengaruhi efektivitas pelaksanaan kegiatan secara keseluruhan. Oleh karena itu, diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam kelingkungan kerja. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan, sebaiknya disampaikan secara jelas tepat dan tepat waktu kepada pihak yang berkepentingan. Selain itu setiap bagian juga diharapkan dapat memberikan laporan perkembangan pekerjaan secara berkala sehingga setiap kendala yang muncul dapat segera diketahui dan dicari solusinya bersama Koordinasi yang baik tidak hanya berarti penyampaian informasi Tetapi juga mencakup kemampuan untuk bekerjasama Saling mendukung dan menghargai peran masing-masing anggota tim Dengan adanya sikap saling terbuka dan saling membantu, proses kerja akan menjadi lebih lancar dan tujuan yang telah ditetapkan dapat dicapai dengan lebih mudah. Kerja sama yang baik juga dapat mengurangi kesalahan komunikasi yang sering menjadi penyebab terjadinya keterlambatan atau hambatan dalam pekerjaan. Selain itu, pemanfaatan teknologi juga dapat menjadi salah satu sarana untuk meningkatkan koordinasi Berbagai platform komunikasi dan sistem digital yang tersedia saat ini dapat digunakan untuk mempermudah penyampaian informasi pemantuan progres pekerjaan serta dokumentasi kegiatan Dengan memanfaatkan teknologi secara optimal Proses komunikasi dapat berlangsung lebih cepat dan efisien Sehingga pekerjaan dapat diselesaikan dengan lebih baik Saya berharap melalui pembahasan pada rapat hari ini kita semua dapat semakin menyadari pentingnya koordinasi dan komunikasi dalam mendukung keberhasilan pekerjaan. Marilah kita bersama-sama meningkatkan kerja sama, memperkuat komunikasi, dan membangun lingkungan kerja yang lebih produktif agar setiap target yang telah ditetapkan dapat tercapai secara maksimal. Demikian yang dapat saya sampaikan terima kasih atas perhatian dan kerja sama dari seluruh peserta rapat semoga hasil diskusi pada hari ini dapat memberikan manfaat bagi peningkatan kinerja kita bersama Wassalamualaikum Wr Wb Terima kasih.
"""

small = """
Assalamualaikum warahmatullahi wabarakatuh Selamat pagi dan salam sejahtera untuk kita semua Pertama-tama, marilah kita panjatkan puji dan syukur kehadiran Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah meluangkan waktu untuk hadir dan berpartisipasi dalam rapat ini Pada kesempatan kali ini, kita akan membahas satu topik utama, yaitu peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan Topik ini sangat penting karena koordinasi yang baik merupakan salah satu faktor utama yang menentukan keberhasilan suatu kegiatan maupun pencapaian target organisasi. Tanpa adanya komunikasi yang efektif dan kerjasama yang baik berbagai tugas yang telah direncanakan dapat mengalami hambatan dalam pelaksanaannya Berdasarkan hasil evaluasi beberapa kegiatan yang telah dilaksanakan sebelumnya, dapat diketahui bahwa sebagian besar program kerja telah berjalan sesuai dengan rencana. Namun, masih terdapat beberapa kendala yang berkaitan dengan proses koordinasi antarabagian Misalnya, pembaruan terkait perkembangan pekerjaan Serta adanya perbedaan pemahaman mengenai tugas dan tanggung jawab masing-masing Hal-hal tersebut meskipun terlihat sederhana dapat memengaruhi efektivitas pelaksanaan kegiatan secara keseluruhan. Oleh karena itu, diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam kelingkungan kerja. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan, sebaiknya disampaikan secara jelas tepat dan tepat waktu kepada pihak yang berkepentingan. Selain itu setiap bagian juga diharapkan dapat memberikan laporan perkembangan pekerjaan secara berkala sehingga setiap kendala yang muncul dapat segera diketahui dan dicari solusinya bersama Koordinasi yang baik tidak hanya berarti penyampaian informasi Tetapi juga mencakup kemampuan untuk bekerjasama Saling mendukung dan menghargai peran masing-masing anggota tim Dengan adanya sikap saling terbuka dan saling membantu, proses kerja akan menjadi lebih lancar dan tujuan yang telah ditetapkan dapat dicapai dengan lebih mudah. Kerjasama yang baik juga dapat mengurangi kesalahan komunikasi yang sering menjadi penyebab terjadinya keterlambatan atau hambatan dalam pekerjaan. Selain itu, pemanfaatan teknologi juga dapat menjadi salah satu sarana untuk meningkatkan koordinasi Berbagai platform komunikasi dan sistem digital yang tersedia saat ini dapat digunakan untuk mempermudah penyampaian informasi pemantuan progres pekerjaan serta dokumentasi kegiatan Dengan memanfaatkan teknologi secara optimal Proses komunikasi dapat berlangsung lebih cepat dan efisien Sehingga pekerjaan dapat diselesaikan dengan lebih baik Saya berharap melalui pembahasan pada rapat hari ini kita semua dapat semakin menyadari pentingnya koordinasi dan komunikasi dalam mendukung keberhasilan pekerjaan. Marilah kita bersama-sama meningkatkan kerjasama, memperkuat komunikasi, dan membangun lingkungan kerja yang lebih produktif agar setiap target yang telah ditetapkan dapat tercapai secara maksimal. demikian yang dapat saya sampaikan terima kasih atas perhatian dan kerjasama dari seluruh peserta rapat semoga hasil diskusi pada hari ini dapat memberikan manfaat bagi peningkatan kinerja kita bersama Wassalamualaikum Wr Wb Terima kasih.
"""

base = """
Assalamualaikum warahmatullahi wabarakatuh Selamat pagi dan salam sejahtera untuk kita semua Pertama-tama, marilah kita panjatkan puji dan syukur kehadiran Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah meluangkan waktu untuk hadir dan berpartisipasi dalam rapat ini Pada kesempatan kali ini, kita akan membahas satu topik utama, yaitu peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan Topik ini sangat penting karena koordinasi yang baik merupakan salah satu faktor utama yang menentukan keberhasilan suatu kegiatan maupun pencapaian target organisasi. Tanpa adanya komunikasi yang efektif dan kerjasama yang baik berbagai tugas yang telah direncanakan dapat mengalami hambatan dalam pelaksanaannya Berdasarkan hasil evaluasi beberapa kegiatan yang telah dilaksanakan sebelumnya, dapat diketahui bahwa sebagian besar program kerja telah berjalan sesuai dengan rencana. Namun, masih terdapat beberapa kendala yang berkaitan dengan proses koordinasi antarabagian Misalnya, pembaruan terkait perkembangan pekerjaan Serta adanya perbedaan pemahaman mengenai tugas dan tanggung jawab masing-masing Hal-hal tersebut meskipun terlihat sederhana dapat memengaruhi efektivitas pelaksanaan kegiatan secara keseluruhan. Oleh karena itu, diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam kelingkungan kerja. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan, sebaiknya disampaikan secara jelas tepat dan tepat waktu kepada pihak yang berkepentingan. Selain itu setiap bagian juga diharapkan dapat memberikan laporan perkembangan pekerjaan secara berkala sehingga setiap kendala yang muncul dapat segera diketahui dan dicari solusinya bersama Koordinasi yang baik tidak hanya berarti penyampaian informasi Tetapi juga mencakup kemampuan untuk bekerjasama Saling mendukung dan menghargai peran masing-masing anggota tim Dengan adanya sikap saling terbuka dan saling membantu, proses kerja akan menjadi lebih lancar dan tujuan yang telah ditetapkan dapat dicapai dengan lebih mudah. Kerjasama yang baik juga dapat mengurangi kesalahan komunikasi yang sering menjadi penyebab terjadinya keterlambatan atau hambatan dalam pekerjaan. Selain itu, pemanfaatan teknologi juga dapat menjadi salah satu sarana untuk meningkatkan koordinasi Berbagai platform komunikasi dan sistem digital yang tersedia saat ini dapat digunakan untuk mempermudah penyampaian informasi pemantuan progres pekerjaan serta dokumentasi kegiatan Dengan memanfaatkan teknologi secara optimal Proses komunikasi dapat berlangsung lebih cepat dan efisien Sehingga pekerjaan dapat diselesaikan dengan lebih baik Saya berharap melalui pembahasan pada rapat hari ini kita semua dapat semakin menyadari pentingnya koordinasi dan komunikasi dalam mendukung keberhasilan pekerjaan. Marilah kita bersama-sama meningkatkan kerjasama, memperkuat komunikasi, and membangun lingkungan kerja yang lebih produktif agar setiap target yang telah ditetapkan dapat tercapai secara maksimal. demikian yang dapat saya sampaikan terima kasih atas perhatian dan kerjasama dari seluruh peserta rapat semoga hasil diskusi pada hari ini dapat memberikan manfaat bagi peningkatan kinerja kita bersama Wassalamualaikum Wr Wb Terima kasih.
"""

tiny = """
Assalamualaikum warahmatullahi wabarakatuh Selamat pagi dan salam sejahtera untuk kita semua Pertama-tama, marilah kita panjatkan puji dan syukur kehadiran Tuhan Yang Maha Esa karena atas rahmat dan karunianya kita dapat berkumpul dan mengikuti rapat koordinasi pada hari ini dalam keadaan sehat Saya juga mengucapkan terima kasih kepada seluruh peserta yang telah meluangkan waktu untuk hadir dan berpartisipasi dalam rapat ini Pada kesempatan kali ini, kita akan membahas satu topik utama, yaitu peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan Topik ini sangat penting karena koordinasi yang baik merupakan salah satu faktor utama yang menentukan keberhasilan suatu kegiatan maupun pencapaian target organisasi. Tanpa adanya komunikasi yang efektif dan kerjasama yang baik berbagai tugas yang telah direncanakan dapat mengalami hambatan dalam pelaksanaannya Berdasarkan hasil evaluasi beberapa kegiatan yang telah dilaksanakan sebelumnya, dapat diketahui bahwa sebagian besar program kerja telah berjalan sesuai dengan rencana. Namun, masih terdapat beberapa kendala yang berkaitan dengan proses koordinasi antarabagian Misalnya, pembaruan terkait perkembangan pekerjaan Serta adanya perbedaan pemahaman mengenai tugas dan tanggung jawab masing-masing Hal-hal tersebut meskipun terlihat sederhana dapat memengaruhi efektivitas pelaksanaan kegiatan secara keseluruhan. Oleh karena itu, diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam kelingkungan kerja. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan, sebaiknya disampaikan secara jelas tepat dan tepat waktu kepada pihak yang berkepentingan. Selain itu setiap bagian juga diharapkan dapat memberikan laporan perkembangan pekerjaan secara berkala sehingga setiap kendala yang muncul dapat segera diketahui dan dicari solusinya bersama Koordinasi yang baik tidak hanya berarti penyampaian informasi Tetapi juga mencakup kemampuan untuk bekerjasama Saling mendukung dan menghargai peran masing-masing anggota tim Dengan adanya sikap saling terbuka dan saling membantu, proses kerja akan menjadi lebih lancar dan tujuan yang telah ditetapkan dapat dicapai dengan lebih mudah. Kerjasama yang baik juga dapat mengurangi kesalahan komunikasi yang sering menjadi penyebab terjadinya keterlambatan atau hambatan dalam pekerjaan. Selain itu, pemanfaatan teknologi juga dapat menjadi salah satu sarana untuk meningkatkan koordinasi Berbagai platform komunikasi dan sistem digital yang tersedia saat ini dapat digunakan untuk mempermudah penyampaian informasi pemantuan progres pekerjaan serta dokumentasi kegiatan Dengan memanfaatkan teknologi secara optimal Proses komunikasi dapat berlangsung lebih cepat dan efisien Sehingga pekerjaan dapat diselesaikan dengan lebih baik Saya berharap melalui pembahasan pada rapat hari ini kita semua dapat semakin menyadari pentingnya koordinasi dan komunikasi dalam mendukung keberhasilan pekerjaan. Marilah kita bersama-sama meningkatkan kerjasama, memperkuat komunikasi, dan membangun lingkungan kerja yang lebih produktif agar setiap target yang telah ditetapkan dapat tercapai secara maksimal. demikian yang dapat saya sampaikan terima kasih atas perhatian dan kerjasama dari seluruh peserta rapat semoga hasil diskusi pada hari ini dapat memberikan manfaat bagi peningkatan kinerja kita bersama Wassalamualaikum Wr Wb Terima kasih.
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