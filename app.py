from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
import os
from werkzeug.utils import secure_filename
from services.filter_service import clean_transcript
from services.summary_service import summarize_text
from services.notulensi_service import generate_notulensi
from datetime import datetime
from flask_mail import Mail, Message
from xhtml2pdf import pisa
from flask import make_response
from collections import OrderedDict
from sqlalchemy import extract
import base64
from services.transkripsi_service import transcribe_audio, transcribe_audio_with_segments, transcribe_audio_complete
from services.diarization_service import diarize_audio, assign_speakers_to_transcript, format_speaker_transcript
from datetime import timedelta
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=6)

app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER
mail = Mail(app)

# =========================
# DATABASE
# =========================
conn = pymysql.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

def get_cursor():
    conn.ping(reconnect=True)
    return conn.cursor(pymysql.cursors.DictCursor)



def get_logo_base64():
    path = os.path.join(app.root_path, 'static', 'images', 'logo.png')
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# =========================
# DIARIZATION
# =========================
#def format_diarization_result(diarization_result):
 #   hasil = []
  #  for item in diarization_result:
   #     speaker = item["speaker"]
    #   end = item["end"]
     #   hasil.append(f"{speaker} ({start}s - {end}s)")
    #return "\n".join(hasil)

# =========================
# UPLOAD
# =========================
UPLOAD_FOLDER = "uploads/audio"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "mp4"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# FORMAT TANGGAL
# =========================
def format_tanggal_indo(tanggal_obj):
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

    hasil = tanggal_obj.strftime("%d %B %Y")
    for en, idn in bulan_indo.items():
        hasil = hasil.replace(en, idn)
    return hasil

# =========================
# EMAIL UNDANGAN
# =========================
def kirim_email_undangan(to_email, kegiatan, tanggal, waktu, tempat, peserta, pdf_path=None):
    try:
        msg = Message(
            subject=f"Undangan: {kegiatan}",
            recipients=[to_email],
            html=f"""
            <p>Yth. {peserta},</p>
            <p>Terlampir kami kirimkan surat undangan kegiatan <b>{kegiatan}</b>.</p>
            <p>Terima kasih.</p>
            <p><b>Admin SIRANA KEMBANG</b></p>
            """
        )

        if pdf_path:
            with open(pdf_path, "rb") as f:
                msg.attach(
                    filename=os.path.basename(pdf_path),
                    content_type="application/pdf",
                    data=f.read()
                )

        mail.send(msg)
        print("Email berhasil dikirim ke", to_email)

    except Exception as e:
        print("Gagal kirim email:", e)

# =========================
# PDF UNDANGAN
# =========================
def render_undangan_html(data_undangan, nama_penerima):
    nomor_surat = f"001/UND/KEMENAG/{data_undangan['id']:03d}"
    tanggal_surat = format_tanggal_indo(datetime.now())
    tanggal_acara = format_tanggal_indo(data_undangan["tanggal"])

    return render_template(
        "pdf/undangan_pdf.html",
        logo_base64=get_logo_base64(),
        undangan={
            "nomor_surat": nomor_surat,
            "tanggal_surat": tanggal_surat,
            "kegiatan": data_undangan["kegiatan"],
            "peserta": nama_penerima,
            "tanggal_acara": tanggal_acara,
            "waktu": str(data_undangan["waktu"])[:5] + " WIB",
            "tempat": data_undangan["tempat"]
        }
    )

def generate_pdf_undangan(data_undangan, nama_penerima):
    html_string = render_undangan_html(data_undangan, nama_penerima)

    output_folder = "outputs/undangan"
    os.makedirs(output_folder, exist_ok=True)

    nama_file_aman = nama_penerima.replace(" ", "_")
    pdf_path = os.path.join(
        output_folder,
        f"undangan_{data_undangan['id']}_{nama_file_aman}.pdf"
    )

    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)

    if pisa_status.err:
        raise Exception("Gagal membuat PDF undangan")

    return pdf_path

# =========================
# HALAMAN AWAL
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = get_cursor()
        cursor.execute(
            "SELECT id, email, role FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            session.permanent = True  # 🔥 WAJIB

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            return "Email atau password salah"

    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

# =========================
# USER - DASHBOARD
# =========================
@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()

    cursor.execute("""
        SELECT id, kegiatan, tanggal, waktu, tempat, status
        FROM undangan
        WHERE user_id = %s
        ORDER BY tanggal_dibuat DESC
        LIMIT 2
    """, (session["user_id"],))
    undangan_terakhir = cursor.fetchall()

    cursor.execute("""
        SELECT n.id, k.nama_kegiatan AS kegiatan, k.tempat, k.waktu, n.file_path
        FROM notulensi n
        JOIN kegiatan k ON n.kegiatan_id = k.id
        WHERE k.created_by = %s
        ORDER BY k.waktu DESC
        LIMIT 2
    """, (session["user_id"],))
    notulensi_terakhir = cursor.fetchall()

    return render_template(
        "user/dashboard.html",
        undangan_terakhir=undangan_terakhir,
        notulensi_terakhir=notulensi_terakhir
    )

# =========================
# USER - BUAT UNDANGAN
# =========================
@app.route("/user/buat-undangan", methods=["GET", "POST"])
def buat_undangan():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT id, nama_kategori
        FROM kategori_undangan
        WHERE nama_kategori IS NOT NULL AND nama_kategori != ''
        ORDER BY nama_kategori ASC
    """)
    kategori_list = cursor.fetchall()
    print("DEBUG kategori_list:", kategori_list)

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
            peserta = peserta_lainnya.strip()

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
            tanggal_input=tanggal_input,
            kategori_list=kategori_list
        )

    return render_template("user/buat-undangan.html", kategori_list=kategori_list)

# =========================
# USER - KIRIM UNDANGAN
# =========================
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
# USER - EDIT UNDANGAN
# =========================
@app.route("/user/edit-undangan/<int:id>", methods=["GET", "POST"])
def edit_undangan(id):
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

    if undangan["status"] != "pending":
        flash("Hanya undangan pending yang bisa diedit.", "warning")
        return redirect(url_for("riwayat_undangan"))

    if request.method == "POST":
        kegiatan = request.form.get("kegiatan")
        tempat = request.form.get("tempat")
        tanggal_input = request.form.get("tanggal")
        waktu = request.form.get("waktu")
        peserta = request.form.get("peserta")

        cursor.execute("""
            UPDATE undangan
            SET kegiatan = %s,
                tempat = %s,
                tanggal = %s,
                waktu = %s,
                peserta = %s,
                updated_at = NOW(),
                updated_by = %s,
                version = version + 1
            WHERE id = %s AND status = 'pending'
        """, (kegiatan, tempat, tanggal_input, waktu, peserta, session["user_id"], id))

        changes = []
        if undangan["kegiatan"] != kegiatan:
            changes.append(("kegiatan", undangan["kegiatan"], kegiatan))
        if undangan["tempat"] != tempat:
            changes.append(("tempat", undangan["tempat"], tempat))
        if str(undangan["tanggal"]) != tanggal_input:
            changes.append(("tanggal", str(undangan["tanggal"]), tanggal_input))
        if undangan["waktu"] != waktu:
            changes.append(("waktu", undangan["waktu"], waktu))
        if undangan["peserta"] != peserta:
            changes.append(("peserta", undangan["peserta"], peserta))

        for field_name, old_value, new_value in changes:
            cursor.execute("""
                INSERT INTO undangan_history (undangan_id, field_name, old_value, new_value, changed_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (id, field_name, old_value, new_value, session["user_id"]))

        conn.commit()

        flash("Undangan berhasil diperbarui.", "success")
        return redirect(url_for("riwayat_undangan"))

    return render_template("user/edit-undangan.html", undangan=undangan)

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
        kegiatan = request.form.get("kegiatan", "").strip()
        tempat = request.form.get("tempat", "").strip()
        peserta = request.form.get("peserta", "").strip()
        jenis_proses = request.form.get("jenis_proses", "transkrip").strip()
        file = request.files.get("audio")

        transkrip_asli = ""
        transkrip_bersih = ""
        hasil_ringkasan = ""
        diarization_text = ""
        hasil_notulensi = ""
        notulensi_path = None

        if not file or file.filename == "":
            return render_template(
                "user/notulensi.html",
                message="Pilih file audio dulu",
                hasil_notulensi=None,
                transkrip_asli=None,
                transkrip_bersih=None,
                hasil_ringkasan=None,
                diarization_text=None,
                file_path=None
            )

        if not allowed_file(file.filename):
            return render_template(
                "user/notulensi.html",
                message="Format file harus mp3, wav, mp4 atau m4a",
                hasil_notulensi=None,
                transkrip_asli=None,
                transkrip_bersih=None,
                hasil_ringkasan=None,
                diarization_text=None,
                file_path=None
            )

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        cursor = conn.cursor()

        try:
            # Simpan kegiatan
            cursor.execute(
                """
                INSERT INTO kegiatan (nama_kegiatan, deskripsi, tempat, waktu, created_by)
                VALUES (%s, %s, %s, NOW(), %s)
                """,
                (kegiatan, "-", tempat, session["user_id"])
            )
            conn.commit()
            kegiatan_id = cursor.lastrowid

            # Simpan peserta
            if peserta:
                daftar_peserta = [p.strip() for p in peserta.split(",") if p.strip()]
                for p in daftar_peserta:
                    cursor.execute(
                        "INSERT INTO peserta (kegiatan_id, nama) VALUES (%s, %s)",
                        (kegiatan_id, p)
                    )
                conn.commit()

            # Simpan rekaman
            cursor.execute(
                "INSERT INTO rekaman (kegiatan_id, file_path) VALUES (%s, %s)",
                (kegiatan_id, filepath)
            )
            conn.commit()
            rekaman_id = cursor.lastrowid

            transcript_segments = []

            # =========================
            # MODE 1: TRANSKRIP SAJA (FAST)
            # =========================
            if jenis_proses == "transkrip":
                try:
                    transkrip_asli = transcribe_audio(filepath) or ""
                except Exception as e:
                    print("ERROR TRANSKRIPSI:", e)
                    transkrip_asli = ""

                try:
                    transkrip_bersih = clean_transcript(transkrip_asli) or transkrip_asli
                except Exception as e:
                    print("ERROR FILTER:", e)
                    transkrip_bersih = transkrip_asli

            # =========================
            # MODE 2: TRANSKRIP + SUMMARY
            # =========================
            elif jenis_proses == "summary":
                try:
                    transkrip_asli = transcribe_audio(filepath) or ""
                except Exception as e:
                    print("ERROR TRANSKRIPSI:", e)
                    transkrip_asli = ""

                try:
                    transkrip_bersih = clean_transcript(transkrip_asli) or transkrip_asli
                except Exception as e:
                    print("ERROR FILTER:", e)
                    transkrip_bersih = transkrip_asli

                try:
                    hasil_ringkasan = summarize_text(transkrip_bersih)
                    if not hasil_ringkasan:
                        hasil_ringkasan = "Tidak ada ringkasan yang berhasil dibuat."
                except Exception as e:
                    print("ERROR SUMMARY:", e)
                    hasil_ringkasan = "Tidak ada ringkasan yang berhasil dibuat."

            # =========================
            # MODE 3: TRANSKRIP + DIARIZATION
            # =========================
            elif jenis_proses == "diarization":
                try:
                    # Satu panggilan saja untuk text + segments
                    transkrip_result = transcribe_audio_complete(filepath)
                    transkrip_asli = transkrip_result["text"]
                    transcript_segments = transkrip_result["segments"]
                except Exception as e:
                    print("ERROR TRANSKRIPSI:", e)
                    transkrip_asli = ""
                    transcript_segments = []

                try:
                    transkrip_bersih = clean_transcript(transkrip_asli) or transkrip_asli
                except Exception as e:
                    print("ERROR FILTER:", e)
                    transkrip_bersih = transkrip_asli

                try:
                    diarization_result = diarize_audio(filepath)

                    if diarization_result["success"]:
                        speaker_transcript = assign_speakers_to_transcript(
                            diarization_result["segments"],
                            transcript_segments
                        )
                        diarization_text = format_speaker_transcript(speaker_transcript)
                    else:
                        diarization_text = "Diarization tidak berhasil diproses."
                except Exception as e:
                    print("ERROR DIARIZATION:", e)
                    diarization_text = "Diarization tidak berhasil diproses."

            else:
                return render_template(
                    "user/notulensi.html",
                    message="Jenis proses tidak valid.",
                    hasil_notulensi=None,
                    transkrip_asli=None,
                    transkrip_bersih=None,
                    hasil_ringkasan=None,
                    diarization_text=None,
                    file_path=None
                )

            # Tentukan isi ringkasan untuk DB
            ringkasan_db = hasil_ringkasan if hasil_ringkasan else "-"

            # Generate file notulensi
            try:
                notulensi_path, isi_notulensi = generate_notulensi(
                    filename=filename,
                    kegiatan=kegiatan,
                    tempat=tempat,
                    peserta=peserta,
                    diarization_text=diarization_text,
                    transkrip_asli=transkrip_asli,
                    transkrip_bersih=transkrip_bersih,
                    ringkasan=hasil_ringkasan,
                    jenis_proses=jenis_proses
                )
                hasil_notulensi = isi_notulensi
            except Exception as e:
                return render_template(
                    "user/notulensi.html",
                    message=f"Gagal membuat dokumen notulensi: {str(e)}",
                    diarization_text=diarization_text,
                    transkrip_asli=transkrip_asli,
                    transkrip_bersih=transkrip_bersih,
                    hasil_ringkasan=hasil_ringkasan,
                    hasil_notulensi="",
                    file_path=None
                )

            # Simpan notulensi ke database
            cursor.execute(
                """
                INSERT INTO notulensi (kegiatan_id, rekaman_id, file_path, ringkasan)
                VALUES (%s, %s, %s, %s)
                """,
                (kegiatan_id, rekaman_id, notulensi_path, ringkasan_db)
            )
            conn.commit()

            pesan_map = {
                "transkrip": "Transkripsi berhasil dibuat.",
                "summary": "Transkripsi dan ringkasan berhasil dibuat.",
                "diarization": "Transkripsi dan diarization berhasil dibuat."
            }

            return render_template(
                "user/notulensi.html",
                message=pesan_map.get(jenis_proses, "Notulensi berhasil dibuat."),
                hasil_notulensi=hasil_notulensi,
                transkrip_asli=transkrip_asli,
                transkrip_bersih=transkrip_bersih,
                hasil_ringkasan=hasil_ringkasan,
                diarization_text=diarization_text,
                file_path=notulensi_path
            )

        except Exception as e:
            conn.rollback()
            print("ERROR NOTULENSI:", e)
            return render_template(
                "user/notulensi.html",
                message=f"Terjadi kesalahan: {str(e)}",
                hasil_notulensi=hasil_notulensi,
                transkrip_asli=transkrip_asli,
                transkrip_bersih=transkrip_bersih,
                hasil_ringkasan=hasil_ringkasan,
                diarization_text=diarization_text,
                file_path=notulensi_path
            )

        finally:
            cursor.close()

    return render_template(
        "user/notulensi.html",
        hasil_notulensi=None,
        transkrip_asli=None,
        transkrip_bersih=None,
        hasil_ringkasan=None,
        diarization_text=None,
        file_path=None
    )

# =========================
# ADMIN - DASHBOARD
# =========================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()

    # =========================
    # STATISTIK UTAMA
    # =========================
    cursor.execute("SELECT COUNT(*) AS total_pending FROM undangan WHERE status = 'pending'")
    total_pending = cursor.fetchone()["total_pending"]

    cursor.execute("SELECT COUNT(*) AS total_approved FROM undangan WHERE status = 'approved'")
    total_approved = cursor.fetchone()["total_approved"]

    cursor.execute("SELECT COUNT(*) AS total_aktivitas FROM undangan")
    total_aktivitas = cursor.fetchone()["total_aktivitas"]

    # =========================
    # AKTIVITAS TERBARU
    # =========================
    cursor.execute("""
        SELECT kegiatan, tanggal, waktu, tempat
        FROM undangan
        ORDER BY tanggal_dibuat DESC
        LIMIT 5
    """)
    aktivitas_terbaru = cursor.fetchall()

    # =========================
    # STATISTIK BULAN INI & LALU
    # =========================
    cursor.execute("""
        SELECT COUNT(*) AS total_bulan_ini
        FROM undangan
        WHERE MONTH(tanggal_dibuat) = MONTH(CURRENT_DATE())
        AND YEAR(tanggal_dibuat) = YEAR(CURRENT_DATE())
    """)
    total_bulan_ini = cursor.fetchone()["total_bulan_ini"]

    cursor.execute("""
        SELECT COUNT(*) AS total_bulan_lalu
        FROM undangan
        WHERE MONTH(tanggal_dibuat) = MONTH(CURRENT_DATE() - INTERVAL 1 MONTH)
        AND YEAR(tanggal_dibuat) = YEAR(CURRENT_DATE() - INTERVAL 1 MONTH)
    """)
    total_bulan_lalu = cursor.fetchone()["total_bulan_lalu"]

    # =========================
    # DATA CHART PER BULAN
    # =========================
    cursor.execute("""
        SELECT 
            MONTH(tanggal_dibuat) AS bulan,
            COUNT(*) AS jumlah
        FROM undangan
        WHERE YEAR(tanggal_dibuat) = YEAR(CURRENT_DATE())
        GROUP BY MONTH(tanggal_dibuat)
        ORDER BY bulan
    """)
    hasil = cursor.fetchall()

    bulan_nama = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    data_bulanan = [0] * 12

    for row in hasil:
        index = int(row["bulan"]) - 1
        data_bulanan[index] = row["jumlah"]

    # =========================
    # RENDER
    # =========================
    return render_template(
        "admin/dashboard.html",
        total_pending=total_pending,
        total_approved=total_approved,
        total_aktivitas=total_aktivitas,
        aktivitas_terbaru=aktivitas_terbaru,
        total_bulan_ini=total_bulan_ini,
        total_bulan_lalu=total_bulan_lalu,
        chart_labels=bulan_nama,
        chart_data=data_bulanan
    )

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
        SELECT *
        FROM undangan
        WHERE id = %s
    """, (id,))
    data = cursor.fetchone()

    if not data:
        flash("Undangan tidak ditemukan.", "danger")
        return redirect(url_for("admin_approval"))

    cursor.execute("""
        UPDATE undangan
        SET status = 'approved', catatan_admin = NULL
        WHERE id = %s
    """, (id,))
    conn.commit()

    cursor.execute("""
    SELECT m.nama, m.email
    FROM master_peserta_undangan m
    LEFT JOIN kategori_undangan k ON m.kategori_id = k.id
    WHERE k.nama_kategori = %s
    """, (data["peserta"],))
    daftar_penerima = cursor.fetchall()

    for p in daftar_penerima:
        pdf_path = generate_pdf_undangan(data, p["nama"])
        kirim_email_undangan(
            to_email=p["email"],
            kegiatan=data["kegiatan"],
            tanggal=data["tanggal"],
            waktu=data["waktu"],
            tempat=data["tempat"],
            peserta=p["nama"],
            pdf_path=pdf_path
        )

    flash("Undangan berhasil disetujui dan email dikirim ke peserta.", "success")
    return redirect(url_for("admin_approval"))

# =========================
# ADMIN - PDF PREVIEW
# =========================
@app.route('/admin/undangan/<int:id>/pdf')
def preview_pdf_undangan(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("SELECT * FROM undangan WHERE id = %s", (id,))
    undangan = cursor.fetchone()

    if not undangan:
        flash("Undangan tidak ditemukan.", "danger")
        return redirect(url_for("admin_approval"))

    html = render_undangan_html(undangan, undangan["peserta"])

    response = make_response()
    response.headers["Content-Type"] = "application/pdf"
    pisa.CreatePDF(html, dest=response)

    return response

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

    cursor = get_cursor()

    cursor.execute("""
        SELECT 
            u.email AS pembuat,
            'Undangan' AS aktivitas,
            un.kegiatan AS judul,
            un.tanggal_dibuat AS tanggal
        FROM undangan un
        LEFT JOIN users u ON un.user_id = u.id
    """)
    data_undangan = cursor.fetchall()

    cursor.execute("""
        SELECT 
            u.email AS pembuat,
            'Notulensi' AS aktivitas,
            k.nama_kegiatan AS judul,
            k.waktu AS tanggal
        FROM notulensi n
        JOIN kegiatan k ON n.kegiatan_id = k.id
        LEFT JOIN users u ON k.created_by = u.id
    """)
    data_notulensi = cursor.fetchall()

    aktivitas = data_undangan + data_notulensi

    aktivitas = sorted(
        aktivitas,
        key=lambda x: x["tanggal"] if x["tanggal"] else "",
        reverse=True
    )

    return render_template("admin/monitoring.html", aktivitas=aktivitas)


# =========================
# ADMIN - KELOLA PENERIMA
# =========================
@app.route("/admin/penerima")
def admin_penerima():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()

    cursor.execute("""
        SELECT id, nama_kategori
        FROM kategori_undangan
        ORDER BY nama_kategori ASC
    """)
    kategori_list = cursor.fetchall()

    cursor.execute("""
        SELECT m.id, m.nama, m.email, k.nama_kategori AS kategori
        FROM master_peserta_undangan m
        LEFT JOIN kategori_undangan k ON m.kategori_id = k.id
        ORDER BY k.nama_kategori ASC, m.nama ASC
    """)
    daftar_penerima = cursor.fetchall()

    return render_template(
        "admin/penerima.html",
        daftar_penerima=daftar_penerima,
        kategori_list=kategori_list
    )

@app.route("/admin/kategori/tambah", methods=["POST"])
def tambah_kategori():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    nama_kategori = request.form.get("nama_kategori", "").strip()

    if not nama_kategori:
        flash("Nama kategori wajib diisi.", "warning")
        return redirect(url_for("admin_penerima"))

    cursor = get_cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM kategori_undangan
        WHERE nama_kategori = %s
    """, (nama_kategori,))
    cek = cursor.fetchone()

    if cek["total"] > 0:
        flash("Kategori sudah ada.", "warning")
        return redirect(url_for("admin_penerima"))

    cursor.execute("""
        INSERT INTO kategori_undangan (nama_kategori)
        VALUES (%s)
    """, (nama_kategori,))
    conn.commit()

    flash("Kategori berhasil ditambahkan.", "success")
    return redirect(url_for("admin_penerima"))

@app.route("/admin/penerima/tambah", methods=["POST"])
def tambah_penerima():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    nama = request.form.get("nama", "").strip()
    email = request.form.get("email", "").strip()
    kategori_id = request.form.get("kategori_id", "").strip()

    if not nama or not email or not kategori_id:
        flash("Nama, email, dan kategori wajib diisi.", "warning")
        return redirect(url_for("admin_penerima"))

    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO master_peserta_undangan (nama, email, kategori_id)
        VALUES (%s, %s, %s)
    """, (nama, email, kategori_id))
    conn.commit()

    flash("Penerima berhasil ditambahkan.", "success")
    return redirect(url_for("admin_penerima"))


@app.route("/admin/penerima/hapus/<int:id>", methods=["POST"])
def hapus_penerima(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("DELETE FROM master_peserta_undangan WHERE id = %s", (id,))
    conn.commit()

    flash("Penerima berhasil dihapus.", "success")
    return redirect(url_for("admin_penerima"))

# =========================
# DOWNLOAD NOTULENSI
# =========================
@app.route("/download/<filename>")
def download_notulensi(filename):
    return send_from_directory("outputs/notulensi", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)