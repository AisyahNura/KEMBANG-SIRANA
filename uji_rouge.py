from rouge_score import rouge_scorer
import pandas as pd


def hitung_rouge(reference, prediction):
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=False
    )

    scores = scorer.score(reference, prediction)

    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rouge2": scores["rouge2"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure
    }


def main():
    data = [
        {
            "judul": "Data Uji 1",
            "reference": "Rapat membahas persiapan kegiatan yang meliputi administrasi, penyusunan jadwal, dan pembagian tugas. Pimpinan juga menekankan pentingnya kerja sama antar bagian.",
            "prediction": "Kegiatan utama akan difokuskan pada persiapan administrasi, penyusunan jadwal, dan pembagian tugas kepada seluruh anggota. Pimpinan rapat juga menegaskan pentingnya kerja sama antar bagian."
        },
        {
            "judul": "Data Uji 2",
            "reference": "Rapat membahas jenis data seperti data longitudinal, data panel, dan data space time yang bergantung pada objek penelitian serta memerlukan penanganan khusus.",
            "prediction": "Ini biasanya kita sebut sebagai data longitudinal, data panel atau data space time. Itu sangat tergantung dari objeknya. Ini tentunya butuh juga penanganan-penanganan sendiri."
        },
        {
            "judul": "Data Uji 3",
            "reference": "Pembahasan berfokus pada peningkatan kualitas pembelajaran di sekolah melalui penggunaan metode interaktif dan teknologi digital. Guru diharapkan lebih aktif dalam mengembangkan metode pembelajaran agar siswa lebih memahami materi.",
            "prediction": "Pada pertemuan hari ini dibahas pentingnya peningkatan kualitas pembelajaran di sekolah. Guru diharapkan dapat menggunakan metode pembelajaran yang lebih interaktif agar siswa lebih aktif dalam proses belajar."
        }
    ]

    hasil = []

    for item in data:
        skor = hitung_rouge(item["reference"], item["prediction"])

        hasil.append({
            "judul": item["judul"],
            "reference": item["reference"],
            "prediction": item["prediction"],
            "rouge1": round(skor["rouge1"], 4),
            "rouge2": round(skor["rouge2"], 4),
            "rougeL": round(skor["rougeL"], 4)
        })

    df = pd.DataFrame(hasil)

    print("\n=== HASIL ROUGE PER DATA ===")
    print(df[["judul", "rouge1", "rouge2", "rougeL"]])

    print("\n=== RATA-RATA ROUGE ===")
    print("ROUGE-1:", round(df["rouge1"].mean(), 4))
    print("ROUGE-2:", round(df["rouge2"].mean(), 4))
    print("ROUGE-L:", round(df["rougeL"].mean(), 4))

    df.to_excel("hasil_rouge_3_data.xlsx", index=False)
    print("\nFile berhasil disimpan: hasil_rouge_3_data.xlsx")


if __name__ == "__main__":
    main()