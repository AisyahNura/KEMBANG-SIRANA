from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
import os
from werkzeug.utils import secure_filename
from services.transkripsi_service import transcribe_audio
from services.filter_service import clean_transcript
from services.summary_service import summarize_text
from services.notulensi_service import generate_notulensi
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sirana-kembang-secret-key"

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="kembang_sirana"
)

def get_cursor():
    conn.ping(reconnect=True)
    return conn.cursor(pymysql.cursors.DictCursor)

UPLOAD_FOLDER = "uploads/audio"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "mp4"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, role FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            session["email"] = user[1]
            session["role"] = user[2]

            if user[2] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            return "Email atau password salah"

    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))
    return render_template("user/dashboard.html")


# =========================
# USER - BUAT UNDANGAN
# =========================
@app.route("/user/buat-undangan", methods=["GET", "POST"])
def buat_undangan():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        kegiatan = request.form.get("kegiatan")
        tempat = request.form.get("tempat")
        tanggal_input = request.form.get("tanggal")
        waktu = request.form.get("waktu")
        peserta = request.form.get("peserta")

        kegiatan_lainnya = request.form.get("kegiatan_lainnya")
        tempat_lainnya = request.form.get("tempat_lainnya")
        peserta_lainnya = request.form.get("peserta_lainnya")

        if kegiatan == "Lainnya":
            kegiatan = kegiatan_lainnya

        if tempat == "Lainnya":
            tempat = tempat_lainnya

        if peserta == "Lainnya":
            peserta = peserta_lainnya

        bulan_indo = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember"
        }

        tanggal_obj = datetime.strptime(tanggal_input, "%Y-%m-%d")
        tanggal_format = tanggal_obj.strftime("%d %B %Y")

        for en, idn in bulan_indo.items():
            tanggal_format = tanggal_format.replace(en, idn)

        nomor_surat = "001/UND/KEMENAG/PREVIEW"

        return render_template(
            "user/buat-undangan.html",
            hasil_undangan=True,
            nomor_surat=nomor_surat,
            kegiatan=kegiatan,
            tempat=tempat,
            tanggal=tanggal_format,
            waktu=waktu,
            peserta=peserta,
            tanggal_input=tanggal_input
        )

    return render_template("user/buat-undangan.html")

@app.route("/user/kirim-undangan", methods=["POST"])
def kirim_undangan():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    kegiatan = request.form.get("kegiatan")
    tempat = request.form.get("tempat")
    tanggal_input = request.form.get("tanggal_input")
    waktu = request.form.get("waktu")
    peserta = request.form.get("peserta")

    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO undangan (user_id, kegiatan, tempat, tanggal, waktu, peserta, status, tanggal_dibuat)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())
    """, (session["user_id"], kegiatan, tempat, tanggal_input, waktu, peserta))
    conn.commit()

    flash("Undangan berhasil dikirim ke admin.", "success")
    return redirect(url_for("riwayat_undangan"))

# =========================
# USER - RIWAYAT UNDANGAN
# =========================
@app.route("/user/riwayat-undangan")
def riwayat_undangan():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT * FROM undangan
        WHERE user_id = %s
        ORDER BY tanggal_dibuat DESC
    """, (session["user_id"],))
    data_undangan = cursor.fetchall()

    return render_template("user/riwayat-undangan.html", data_undangan=data_undangan)


# =========================
# USER - PREVIEW UNDANGAN APPROVED
# =========================
@app.route("/user/undangan/<int:id>")
def preview_undangan_user(id):
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT * FROM undangan
        WHERE id = %s AND user_id = %s
    """, (id, session["user_id"]))
    undangan = cursor.fetchone()

    if not undangan:
        flash("Undangan tidak ditemukan.", "danger")
        return redirect(url_for("riwayat_undangan"))

    if undangan["status"] != "approved":
        flash("Undangan belum disetujui admin.", "warning")
        return redirect(url_for("riwayat_undangan"))

    nomor_surat = f"001/UND/KEMENAG/{id:03d}"

    return render_template(
        "user/preview-undangan.html",
        undangan=undangan,
        nomor_surat=nomor_surat,
        tanggal_format=undangan["tanggal"].strftime("%d %B %Y") if undangan["tanggal"] else "-"
    )


# =========================
# USER - NOTULENSI
# =========================
@app.route("/user/notulensi", methods=["GET", "POST"])
def notulensi():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        kegiatan = request.form.get("kegiatan")
        tempat = request.form.get("tempat")
        peserta = request.form.get("peserta")
        file = request.files.get("audio")

        if not file or file.filename == "":
            return render_template("user/notulensi.html", message="Pilih file audio dulu")

        if not allowed_file(file.filename):
            return render_template("user/notulensi.html", message="Format file harus mp3, wav, mp4 atau m4a")

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO kegiatan (nama_kegiatan, deskripsi, tempat, waktu, created_by) VALUES (%s, %s, %s, NOW(), %s)",
            (kegiatan, "-", tempat, session["user_id"])
        )
        conn.commit()
        kegiatan_id = cursor.lastrowid

        if peserta:
            daftar_peserta = [p.strip() for p in peserta.split(",") if p.strip()]
            for p in daftar_peserta:
                cursor.execute(
                    "INSERT INTO peserta (kegiatan_id, nama) VALUES (%s, %s)",
                    (kegiatan_id, p)
                )
            conn.commit()

        cursor.execute(
            "INSERT INTO rekaman (kegiatan_id, file_path) VALUES (%s, %s)",
            (kegiatan_id, filepath)
        )
        conn.commit()
        rekaman_id = cursor.lastrowid

        transkrip_asli = transcribe_audio(filepath)
        transkrip_bersih = clean_transcript(transkrip_asli)
        ringkasan = summarize_text(transkrip_bersih)

        notulensi_path, isi_notulensi = generate_notulensi(
            filename,
            kegiatan,
            tempat,
            peserta,
            transkrip_asli,
            transkrip_bersih,
            ringkasan
        )

        cursor.execute(
            "INSERT INTO notulensi (kegiatan_id, rekaman_id, file_path, ringkasan) VALUES (%s, %s, %s, %s)",
            (kegiatan_id, rekaman_id, notulensi_path, ringkasan)
        )
        conn.commit()

        return render_template(
            "user/notulensi.html",
            message="Rekaman berhasil diupload dan notulensi berhasil dibuat",
            hasil_notulensi=isi_notulensi,
            file_path=notulensi_path
        )

    return render_template("user/notulensi.html")


# =========================
# ADMIN - DASHBOARD
# =========================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin/dashboard.html")


# =========================
# ADMIN - APPROVAL UNDANGAN
# =========================
@app.route("/admin/approval")
def admin_approval():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()

    cursor.execute("""
        SELECT undangan.*, users.email AS pembuat
        FROM undangan
        LEFT JOIN users ON undangan.user_id = users.id
        WHERE undangan.status = 'pending'
        ORDER BY undangan.tanggal_dibuat DESC
    """)
    pending_undangan = cursor.fetchall()

    cursor.execute("""
        SELECT undangan.*, users.email AS pembuat
        FROM undangan
        LEFT JOIN users ON undangan.user_id = users.id
        WHERE undangan.status = 'approved'
        ORDER BY undangan.tanggal_dibuat DESC
    """)
    approved_undangan = cursor.fetchall()

    return render_template(
        "admin/approval.html",
        pending_undangan=pending_undangan,
        approved_undangan=approved_undangan
    )


# =========================
# ADMIN - DETAIL UNDANGAN
# =========================
@app.route("/admin/undangan/<int:id>")
def lihat_undangan_admin(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT undangan.*, users.email AS pembuat
        FROM undangan
        LEFT JOIN users ON undangan.user_id = users.id
        WHERE undangan.id = %s
    """, (id,))
    undangan = cursor.fetchone()

    if not undangan:
        flash("Undangan tidak ditemukan.", "danger")
        return redirect(url_for("admin_approval"))

    nomor_surat = f"001/UND/KEMENAG/{id:03d}"

    return render_template(
        "admin/detail-undangan.html",
        undangan=undangan,
        nomor_surat=nomor_surat,
        tanggal_format=undangan["tanggal"].strftime("%d %B %Y") if undangan["tanggal"] else "-"
    )


# =========================
# ADMIN - SETUJUI UNDANGAN
# =========================
@app.route("/admin/undangan/<int:id>/setujui", methods=["POST"])
def setujui_undangan(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        UPDATE undangan
        SET status = 'approved', catatan_admin = NULL
        WHERE id = %s
    """, (id,))
    conn.commit()

    flash("Undangan berhasil disetujui.", "success")
    return redirect(url_for("admin_approval"))


# =========================
# ADMIN - TOLAK UNDANGAN
# =========================
@app.route("/admin/undangan/<int:id>/tolak", methods=["POST"])
def tolak_undangan(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    catatan_admin = request.form.get("catatan_admin", "Ditolak admin")

    cursor = get_cursor()
    cursor.execute("""
        UPDATE undangan
        SET status = 'rejected', catatan_admin = %s
        WHERE id = %s
    """, (catatan_admin, id))
    conn.commit()

    flash("Undangan ditolak.", "warning")
    return redirect(url_for("admin_approval"))


# =========================
# ADMIN - MONITORING
# =========================
@app.route("/admin/monitoring")
def admin_monitoring():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin/monitoring.html")


@app.route("/download/<filename>")
def download_notulensi(filename):
    return send_from_directory("outputs/notulensi", filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)