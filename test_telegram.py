from telegram_service import kirim_pesan_telegram, kirim_file_telegram

# Tes kirim pesan
hasil = kirim_pesan_telegram("Halo dari SIRANA KEMBANG 🌸")
print(hasil)

# Tes kirim file PDF
hasil_file = kirim_file_telegram(
    "outputs/undangan/undangan_27_Fajar.pdf",
    "Berikut file undangan dari SIRANA KEMBANG"
)
print(hasil_file)