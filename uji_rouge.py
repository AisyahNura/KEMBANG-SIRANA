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
            "judul": "Data Uji 1 (Rapat Koordinasi 1)",
            "reference": "Rapat membahas pentingnya peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan. Seluruh anggota tim diharapkan meningkatkan kualitas komunikasi, menyampaikan informasi secara tepat waktu, serta memperkuat kerja sama antarbagian. Pemanfaatan teknologi juga dianjurkan untuk mendukung penyampaian informasi, pemantauan pekerjaan, dan dokumentasi kegiatan agar tujuan organisasi dapat tercapai secara optimal.",
            "prediction": "Poin Penting:\n1. Diperlukan komitmen dari seluruh anggota tim untuk meningkatkan kualitas komunikasi dalam lingkungan kerja.\n2. Setiap informasi yang berkaitan dengan kegiatan atau pekerjaan sebaiknya disampaikan secara jelas, tepat, dan tepat waktu kepada pihak yang berkepentingan.\n\nKesimpulan:\nRapat koordinasi telah berhasil membahas pentingnya peningkatan koordinasi dan komunikasi dalam pelaksanaan pekerjaan. Dengan meningkatkan kualitas komunikasi dan kerja sama, diharapkan dapat meningkatkan keberhasilan pekerjaan dan mencapai target yang telah ditetapkan secara maksimal."
        },
        {
            "judul": "Data Uji 2 (Rapat Pelayanan Kemenag)",
            "reference": "Rapat membahas peningkatan kualitas pelayanan di lingkungan Kementerian Agama. Seluruh pegawai diharapkan meningkatkan disiplin, profesionalisme, serta koordinasi dalam bekerja. Selain itu, pemanfaatan teknologi informasi perlu dioptimalkan untuk mendukung pelayanan yang lebih cepat, akurat, dan transparan sehingga kualitas pelayanan kepada masyarakat dapat terus meningkat.",
            "prediction": "Poin Penting:\n1. Meningkatkan kualitas pelayanan di Kementerian Agama melalui kerja sama dan keordinasi yang baik antar pegawai dan bagian.\n2. Menggunakan teknologi informasi untuk mendukung pengelolaan data, penyampaian informasi, dan administrasi layanan.\n\nKesimpulan:\nRapat ini berharap dapat meningkatkan kualitas pelayanan di lingkungan Kementerian Agama melalui kerja sama, keordinasi, dan penggunaan teknologi informasi yang efektif. Dengan demikian, diharapkan dapat memberikan pelayanan yang lebih optimal kepada masyarakat dan mencapai tujuan organisasi dengan lebih baik."
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

    df.to_excel("hasil_rouge_2_data.xlsx", index=False)
    print("\nFile berhasil disimpan: hasil_rouge_2_data.xlsx")


if __name__ == "__main__":
    main()