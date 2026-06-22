from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message
from xhtml2pdf import pisa
from flask import make_response
from collections import OrderedDict
from sqlalchemy import extract
import base64
import secrets
import re
import requests
from datetime import timedelta
import config
from services.fonnte_service import kirim_whatsapp_fonnte

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
class LazyMySQLConnection:
    def __init__(self):
        self._conn = None

    def get(self):
        if self._conn is None:
            self._conn = pymysql.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                autocommit=True
            )
        else:
            self._conn.ping(reconnect=True)
        return self._conn

    def __getattr__(self, name):
        return getattr(self.get(), name)


conn = LazyMySQLConnection()

def get_cursor():
    conn.ping(reconnect=True)
    return conn.cursor(pymysql.cursors.DictCursor)


def ensure_undangan_history_table():
    cursor = get_cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS undangan_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                undangan_id INT NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                old_value TEXT NULL,
                new_value TEXT NULL,
                changed_by INT NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_undangan_history_undangan_id (undangan_id),
                INDEX idx_undangan_history_changed_by (changed_by),
                CONSTRAINT fk_undangan_history_undangan
                    FOREIGN KEY (undangan_id) REFERENCES undangan(id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_undangan_history_user
                    FOREIGN KEY (changed_by) REFERENCES users(id)
                    ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    except Exception as e:
        # Keep app startup resilient when DB user lacks schema privileges.
        print("Gagal memastikan tabel undangan_history:", e)


ensure_undangan_history_table()


def ensure_kategori_is_active_column():
    cursor = get_cursor()
    try:
        cursor.execute("""
            ALTER TABLE kategori_undangan
            ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1
        """)
        conn.commit()
    except pymysql.err.ProgrammingError as e:
        # Ignore "duplicate column" error and continue app startup.
        if not (e.args and e.args[0] == 1060):
            print("Gagal memastikan kolom is_active pada kategori_undangan:", e)
    except Exception as e:
        print("Gagal memastikan kolom is_active pada kategori_undangan:", e)


def kategori_has_is_active_column():
    cursor = get_cursor()
    cursor.execute("SHOW COLUMNS FROM kategori_undangan LIKE 'is_active'")
    return cursor.fetchone() is not None


ensure_kategori_is_active_column()


def ensure_undangan_waktu_selesai_column():
    cursor = get_cursor()
    try:
        cursor.execute("""
            ALTER TABLE undangan
            ADD COLUMN waktu_selesai TIME NULL AFTER waktu
        """)
        conn.commit()
    except pymysql.err.ProgrammingError as e:
        # Ignore "duplicate column" error and continue app startup.
        if not (e.args and e.args[0] == 1060):
            print("Gagal memastikan kolom waktu_selesai pada undangan:", e)
    except Exception as e:
        print("Gagal memastikan kolom waktu_selesai pada undangan:", e)


ensure_undangan_waktu_selesai_column()




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
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "mp4", "aac"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def validasi_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(pattern, email):
        return False, "Maaf format email yang dimasukkan tidak valid."

    return True, "Email valid."
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


def format_waktu_rentang(waktu_mulai, waktu_selesai=None, with_wib=False):
    mulai = str(waktu_mulai)[:5] if waktu_mulai else "-"
    selesai = str(waktu_selesai)[:5] if waktu_selesai else ""
    label = f"{mulai} - {selesai}" if selesai else mulai
    return f"{label} WIB" if with_wib else label

# =========================
# EMAIL UNDANGAN
# =========================
def kirim_email_undangan(to_email, kegiatan, tanggal, waktu, tempat, peserta, pdf_path=None, token=None):
    try:
        confirm_link = f"{config.BASE_URL}/kehadiran/{token}" if token else ""

        html_content = f"""
        <p>Yth. {peserta},</p>
        <p>Terlampir kami kirimkan surat undangan kegiatan <b>{kegiatan}</b>.</p>
        {f'<p>Silakan konfirmasi kehadiran Anda melalui link berikut: <a href="{confirm_link}">{confirm_link}</a></p>' if confirm_link else ''}
        <p>Terima kasih.</p>
        <p><b>Admin SIRANA KEMBANG</b></p>
        """

        # Siapkan data untuk Brevo API
        payload = {
            "sender": {
                "name": "SIRANA KEMBANG",
                "email": config.MAIL_DEFAULT_SENDER
            },
            "to": [{"email": to_email, "name": peserta}],
            "subject": f"Undangan: {kegiatan}",
            "htmlContent": html_content
        }

        # Jika ada PDF, lampirkan sebagai attachment (base64)
        if pdf_path:
            with open(pdf_path, "rb") as f:
                import base64 as b64
                pdf_data = b64.b64encode(f.read()).decode("utf-8")
                payload["attachment"] = [{
                    "name": os.path.basename(pdf_path),
                    "content": pdf_data
                }]

        # Kirim via Brevo HTTP API (port 443, tidak diblokir DigitalOcean)
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": config.BREVO_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=payload
        )

        if response.status_code == 201:
            print("Email berhasil dikirim ke", to_email)
        else:
            print("Gagal kirim email ke", to_email, "- Status:", response.status_code, response.text)

    except Exception as e:
        print("Gagal kirim email:", e)

# =========================
# PDF UNDANGAN
# =========================
def render_undangan_html(data_undangan, nama_penerima):
    nomor_surat = f"001/UND/KEMENAG/{data_undangan['id']:03d}"
    tanggal_surat_sumber = data_undangan.get("tanggal_dibuat")
    tanggal_surat = format_tanggal_indo(tanggal_surat_sumber or datetime.now())
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
            "waktu": format_waktu_rentang(
                data_undangan["waktu"],
                data_undangan.get("waktu_selesai"),
                with_wib=True
            ),
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
        SELECT id, kegiatan, tanggal, waktu, waktu_selesai, tempat, status
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

    for item in notulensi_terakhir:
        raw_path = item.get("file_path") or ""
        normalized_path = raw_path.replace("\\", "/")
        item["filename"] = os.path.basename(normalized_path) if normalized_path else ""

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
    if kategori_has_is_active_column():
        cursor.execute("""
            SELECT id, nama_kategori
            FROM kategori_undangan
            WHERE nama_kategori IS NOT NULL
              AND nama_kategori != ''
              AND is_active = 1
            ORDER BY nama_kategori ASC
        """)
    else:
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
        waktu_selesai = request.form.get("waktu_selesai")
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
        tanggal_acara = tanggal_obj.strftime("%d %B %Y")

        for en, idn in bulan_indo.items():
            tanggal_acara = tanggal_acara.replace(en, idn)

        tanggal_surat = format_tanggal_indo(datetime.now())

        nomor_surat = "001/UND/KEMENAG/PREVIEW"

        return render_template(
            "user/buat-undangan.html",
            hasil_undangan=True,
            nomor_surat=nomor_surat,
            kegiatan=kegiatan,
            tempat=tempat,
            tanggal_surat=tanggal_surat,
            tanggal_acara=tanggal_acara,
            waktu=waktu,
            waktu_selesai=waktu_selesai,
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
    waktu_selesai = request.form.get("waktu_selesai")
    peserta = request.form.get("peserta")

    cursor = get_cursor()
    cursor.execute("""
        INSERT INTO undangan (user_id, kegiatan, tempat, tanggal, waktu, waktu_selesai, peserta, status, tanggal_dibuat)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
    """, (session["user_id"], kegiatan, tempat, tanggal_input, waktu, waktu_selesai, peserta))
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
        waktu_selesai = request.form.get("waktu_selesai")
        peserta = request.form.get("peserta")

        cursor.execute("""
            UPDATE undangan
            SET kegiatan = %s,
                tempat = %s,
                tanggal = %s,
                waktu = %s,
                waktu_selesai = %s,
                peserta = %s,
                updated_at = NOW(),
                updated_by = %s,
                version = version + 1
            WHERE id = %s AND status = 'pending'
        """, (kegiatan, tempat, tanggal_input, waktu, waktu_selesai, peserta, session["user_id"], id))

        changes = []
        if undangan["kegiatan"] != kegiatan:
            changes.append(("kegiatan", undangan["kegiatan"], kegiatan))
        if undangan["tempat"] != tempat:
            changes.append(("tempat", undangan["tempat"], tempat))
        if str(undangan["tanggal"]) != tanggal_input:
            changes.append(("tanggal", str(undangan["tanggal"]), tanggal_input))
        if str(undangan["waktu"])[:5] != str(waktu)[:5]:
            changes.append(("waktu", str(undangan["waktu"])[:5], waktu))
        if str(undangan.get("waktu_selesai") or "")[:5] != str(waktu_selesai or "")[:5]:
            changes.append(("waktu_selesai", str(undangan.get("waktu_selesai") or "")[:5], waktu_selesai or ""))
        if undangan["peserta"] != peserta:
            changes.append(("peserta", undangan["peserta"], peserta))

        for field_name, old_value, new_value in changes:
            try:
                cursor.execute("""
                    INSERT INTO undangan_history (undangan_id, field_name, old_value, new_value, changed_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id, field_name, old_value, new_value, session["user_id"]))
            except pymysql.err.ProgrammingError as e:
                if e.args and e.args[0] == 1146:
                    # Table not found: skip audit insert to avoid blocking main update flow.
                    print("Tabel undangan_history belum tersedia, histori perubahan tidak disimpan.")
                    break
                raise

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
        tanggal_surat=format_tanggal_indo(undangan["tanggal_dibuat"]) if undangan.get("tanggal_dibuat") else format_tanggal_indo(datetime.now()),
        tanggal_acara=format_tanggal_indo(undangan["tanggal"]) if undangan["tanggal"] else "-",
        waktu_range=format_waktu_rentang(undangan["waktu"], undangan.get("waktu_selesai"))
    )


# =========================
# USER - NOTULENSI
# =========================
@app.route("/user/notulensi", methods=["GET", "POST"])
def notulensi():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        # Lazy import: avoid loading heavy AI modules when opening the page (GET).
        from services.filter_service import clean_transcript
        from services.notulensi_service import generate_notulensi
        from services.transkripsi_service import transcribe_audio, transcribe_audio_complete

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
                message="Format file harus mp3, wav, mp4, m4a atau aac",
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

        # =====================================================================
        # VALIDASI DURASI AUDIO (Maksimal 60 Menit)
        # =====================================================================
        try:
            from pydub import AudioSegment
            sound = AudioSegment.from_file(filepath)
            durasi_detik = len(sound) / 1000.0
            durasi_menit = durasi_detik / 60.0
            
            if durasi_menit < 1.0 or durasi_menit > 60.0:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                
                # Tentukan pesan error berdasarkan jenis pelanggaran durasi
                pesan_error = "Unggahan ditolak! Durasi audio terlalu pendek." if durasi_menit < 1.0 else "Unggahan ditolak! Durasi audio melebihi batas maksimal 60 menit."
                
                return render_template(
                    "user/notulensi.html",
                    message=pesan_error,
                    hasil_notulensi=None,
                    transkrip_asli=None,
                    transkrip_bersih=None,
                    hasil_ringkasan=None,
                    diarization_text=None,
                    file_path=None
                )
        except Exception as e:
            # Fallback jika pydub gagal membaca agar proses tetap berjalan
            print(f"[Warning] Gagal memvalidasi durasi audio: {e}")

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
                from services.summary_service import summarize_text

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
                from services.diarization_service import (
                    diarize_audio,
                    assign_speakers_to_transcript,
                    format_speaker_transcript,
                )

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
                    # Estimasi jumlah pembicara dari kolom peserta (hanya dipaksa jika lebih dari 1 peserta)
                    peserta_list = [p.strip() for p in peserta.split(",") if p.strip()]
                    num_speakers = len(peserta_list) if len(peserta_list) > 1 else None
                    
                    diarization_result = diarize_audio(filepath, num_speakers=num_speakers)

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


@app.route("/user/riwayat-notulensi")
def riwayat_notulensi():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT n.id, k.nama_kegiatan AS kegiatan, k.tempat, k.waktu,
               n.file_path, n.ringkasan
        FROM notulensi n
        JOIN kegiatan k ON n.kegiatan_id = k.id
        WHERE k.created_by = %s
        ORDER BY k.waktu DESC
    """, (session["user_id"],))
    data_notulensi = cursor.fetchall()

    for item in data_notulensi:
        raw_path = item.get("file_path") or ""
        normalized_path = raw_path.replace("\\", "/")
        item["filename"] = os.path.basename(normalized_path) if normalized_path else ""

    return render_template(
        "user/riwayat-notulensi.html",
        data_notulensi=data_notulensi
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
        SELECT kegiatan, tanggal, waktu, waktu_selesai, tempat
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
        tanggal_surat=format_tanggal_indo(undangan["tanggal_dibuat"]) if undangan.get("tanggal_dibuat") else format_tanggal_indo(datetime.now()),
        tanggal_acara=format_tanggal_indo(undangan["tanggal"]) if undangan["tanggal"] else "-",
        waktu_range=format_waktu_rentang(undangan["waktu"], undangan.get("waktu_selesai"))
    )


# =========================
# ADMIN - SETUJUI UNDANGAN + KIRIM EMAIL & WHATSAPP
# =========================
def proses_setujui_undangan(id, channel="email"):
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
        SELECT m.nama, m.email, m.nomor_hp
        FROM master_peserta_undangan m
        LEFT JOIN kategori_undangan k ON m.kategori_id = k.id
        WHERE k.nama_kategori = %s
    """, (data["peserta"],))
    daftar_penerima = cursor.fetchall()

    if not daftar_penerima:
        flash("Undangan disetujui, tetapi belum ada penerima pada kategori tersebut.", "warning")
        return redirect(url_for("admin_approval"))

    total_email = 0
    total_wa_terkirim = 0
    total_wa_gagal = 0

    for p in daftar_penerima:
        token = secrets.token_urlsafe(32)

        try:
            cursor.execute("""
                INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token)
                VALUES (%s, %s, %s, %s)
            """, (data["id"], p["nama"], p["email"], token))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Gagal menyimpan token konfirmasi untuk", p.get("email"), e)
            continue

        link_konfirmasi = f"{config.BASE_URL}/kehadiran/{token}"

        # =========================
        # KIRIM EMAIL
        # =========================
        if channel in ["email", "semua"]:
            try:
                pdf_path = generate_pdf_undangan(data, p["nama"])

                kirim_email_undangan(
                    to_email=p["email"],
                    kegiatan=data["kegiatan"],
                    tanggal=data["tanggal"],
                    waktu=data["waktu"],
                    tempat=data["tempat"],
                    peserta=p["nama"],
                    pdf_path=pdf_path,
                    token=token
                )

                total_email += 1

            except Exception as e:
                print("Gagal kirim email ke", p.get("email"), e)

        # =========================
        # KIRIM WHATSAPP
        # =========================
        if channel in ["whatsapp", "semua"]:
            print("CHANNEL YANG DIPILIH:", channel)

            # Kalau admin memilih WhatsApp saja,
            # maka pesan WA berisi undangan lengkap.
            if channel == "whatsapp":
                pesan_wa = f"""Assalamu’alaikum Wr. Wb.

Yth. Bapak/Ibu {p['nama']}

Dengan hormat,

Sehubungan dengan akan dilaksanakannya kegiatan berikut:

Nama Kegiatan : {data['kegiatan']}
Hari/Tanggal  : {format_tanggal_indo(data['tanggal'])}
Waktu         : {format_waktu_rentang(data['waktu'], data.get('waktu_selesai'), with_wib=True)}
Tempat        : {data['tempat']}

Dengan ini kami mengundang Bapak/Ibu untuk hadir dan mengikuti kegiatan tersebut.

Untuk melihat detail undangan dan melakukan konfirmasi kehadiran, silakan mengakses tautan berikut:

{link_konfirmasi}

Demikian undangan ini kami sampaikan. Besar harapan kami Bapak/Ibu dapat hadir tepat waktu.
Atas perhatian dan kehadiran Bapak/Ibu, kami ucapkan terima kasih.

Wassalamu’alaikum Wr. Wb.

Hormat kami,
SIRANA KEMBANG
Kantor Kementerian Agama
"""

            # Kalau admin memilih Email & WhatsApp,
            # maka email berisi file undangan resmi,
            # sedangkan WA hanya sebagai pemberitahuan.
            else:
                pesan_wa = f"""Assalamu’alaikum Wr. Wb.

Yth. Bapak/Ibu {p['nama']}

Dengan hormat,

Bersama pesan ini kami sampaikan bahwa Bapak/Ibu diundang untuk menghadiri kegiatan {data['kegiatan']} yang akan dilaksanakan pada:

Hari/Tanggal : {format_tanggal_indo(data['tanggal'])}
Waktu        : {format_waktu_rentang(data['waktu'], data.get('waktu_selesai'), with_wib=True)}
Tempat       : {data['tempat']}

File undangan resmi telah kami kirimkan melalui email. Mohon Bapak/Ibu dapat memeriksa email masuk atau folder spam apabila undangan belum terlihat.

Untuk melakukan konfirmasi kehadiran, silakan mengakses tautan berikut:

{link_konfirmasi}

Demikian informasi ini kami sampaikan. Atas perhatian Bapak/Ibu, kami ucapkan terima kasih.

Wassalamu’alaikum Wr. Wb.

SIRANA KEMBANG
Kantor Kementerian Agama
"""

            hasil_wa = kirim_whatsapp_fonnte(p.get("nomor_hp"), pesan_wa)
            print("HASIL KIRIM WA:", p["nama"], hasil_wa)

            if hasil_wa.get("success"):
                total_wa_terkirim += 1
            else:
                total_wa_gagal += 1

    if channel == "email":
        flash(f"Undangan berhasil disetujui dan email terkirim: {total_email}.", "success")
    elif channel == "whatsapp":
        flash(f"Undangan berhasil disetujui. WhatsApp terkirim: {total_wa_terkirim}, gagal: {total_wa_gagal}.", "success")
    else:
        flash(f"Undangan berhasil disetujui. Email terkirim: {total_email}. WhatsApp terkirim: {total_wa_terkirim}, gagal: {total_wa_gagal}.", "success")

    return redirect(url_for("admin_approval"))


# =========================
# ADMIN - SETUJUI VIA EMAIL
# =========================
@app.route("/admin/undangan/<int:id>/setujui-email", methods=["POST"])
def setujui_undangan_email(id):
    return proses_setujui_undangan(id, channel="email")


# =========================
# ADMIN - SETUJUI VIA WHATSAPP
# =========================
@app.route("/admin/undangan/<int:id>/setujui-whatsapp", methods=["POST"])
def setujui_undangan_whatsapp(id):
    return proses_setujui_undangan(id, channel="whatsapp")


# =========================
# ADMIN - SETUJUI VIA EMAIL & WHATSAPP
# =========================
@app.route("/admin/undangan/<int:id>/setujui-semua", methods=["POST"])
def setujui_undangan_semua(id):
    return proses_setujui_undangan(id, channel="semua")
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

    now = datetime.now()
    try:
        selected_month = int(request.args.get("month", now.month))
    except (TypeError, ValueError):
        selected_month = now.month

    try:
        selected_year = int(request.args.get("year", now.year))
    except (TypeError, ValueError):
        selected_year = now.year

    if selected_month < 1 or selected_month > 12:
        selected_month = now.month

    cursor.execute("""
        SELECT
            un.id,
            un.kegiatan,
            un.tanggal,
            un.waktu,
            un.waktu_selesai,
            un.tempat,
            un.peserta,
            un.status,
            un.tanggal_dibuat,
            u.email AS pembuat
        FROM undangan un
        LEFT JOIN users u ON un.user_id = u.id
        WHERE MONTH(un.tanggal_dibuat) = %s
          AND YEAR(un.tanggal_dibuat) = %s
        ORDER BY un.tanggal_dibuat DESC
    """, (selected_month, selected_year))
    undangan_bulanan = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected
        FROM undangan
        WHERE MONTH(tanggal_dibuat) = %s
          AND YEAR(tanggal_dibuat) = %s
    """, (selected_month, selected_year))
    monthly_summary = cursor.fetchone() or {}

    cursor.execute("""
        SELECT DISTINCT YEAR(tanggal_dibuat) AS tahun
        FROM undangan
        ORDER BY tahun DESC
    """)
    available_years = [row["tahun"] for row in cursor.fetchall() if row.get("tahun")]
    if not available_years:
        available_years = [now.year]
    if selected_year not in available_years:
        available_years.insert(0, selected_year)

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

    aktivitas = list(data_undangan) + list(data_notulensi)
    aktivitas = sorted(
        aktivitas,
        key=lambda x: x["tanggal"] if x["tanggal"] else "",
        reverse=True
    )

    # Statistik konfirmasi kehadiran untuk bulan/taun terpilih
    cursor.execute("""
        SELECT
            SUM(CASE WHEN status_kehadiran = 'hadir' THEN 1 ELSE 0 END) AS hadir,
            SUM(CASE WHEN status_kehadiran = 'tidak_hadir' THEN 1 ELSE 0 END) AS tidak_hadir,
            SUM(CASE WHEN status_kehadiran = 'diwakilkan' THEN 1 ELSE 0 END) AS diwakilkan
        FROM konfirmasi_kehadiran
        WHERE MONTH(created_at) = %s AND YEAR(created_at) = %s
    """, (selected_month, selected_year))
    konfirmasi_stats = cursor.fetchone() or {"hadir": 0, "tidak_hadir": 0, "diwakilkan": 0}

    cursor.execute("""
        SELECT kk.*, u.kegiatan
        FROM konfirmasi_kehadiran kk
        LEFT JOIN undangan u ON kk.undangan_id = u.id
        WHERE MONTH(kk.created_at) = %s AND YEAR(kk.created_at) = %s
        ORDER BY kk.created_at DESC
    """, (selected_month, selected_year))
    konfirmasi_list = cursor.fetchall()

    month_options = [
        (1, "Januari"), (2, "Februari"), (3, "Maret"), (4, "April"),
        (5, "Mei"), (6, "Juni"), (7, "Juli"), (8, "Agustus"),
        (9, "September"), (10, "Oktober"), (11, "November"), (12, "Desember")
    ]

    return render_template(
        "admin/monitoring.html",
        aktivitas=aktivitas,
        undangan_bulanan=undangan_bulanan,
        monthly_summary=monthly_summary,
        selected_month=selected_month,
        selected_year=selected_year,
        month_options=month_options,
        available_years=available_years,
        format_waktu_rentang=format_waktu_rentang,
        konfirmasi_stats=konfirmasi_stats,
        konfirmasi_list=konfirmasi_list
    )


# =========================
# ADMIN - KELOLA PENERIMA
# =========================
@app.route("/admin/penerima")
def admin_penerima():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    cursor = get_cursor()

    if kategori_has_is_active_column():
        cursor.execute("""
            SELECT id, nama_kategori, is_active
            FROM kategori_undangan
            ORDER BY is_active DESC, nama_kategori ASC
        """)
        kategori_manage_list = cursor.fetchall()
        kategori_list = [item for item in kategori_manage_list if item["is_active"] == 1]
    else:
        cursor.execute("""
            SELECT id, nama_kategori
            FROM kategori_undangan
            ORDER BY nama_kategori ASC
        """)
        kategori_list = cursor.fetchall()
        kategori_manage_list = []

    cursor.execute("""
        SELECT m.id, m.nama, m.email, m.nomor_hp, k.nama_kategori AS kategori
        FROM master_peserta_undangan m
        LEFT JOIN kategori_undangan k ON m.kategori_id = k.id
        ORDER BY k.nama_kategori ASC, m.nama ASC
    """)
    daftar_penerima = cursor.fetchall()

    return render_template(
        "admin/penerima.html",
        daftar_penerima=daftar_penerima,
        kategori_list=kategori_list,
        kategori_manage_list=kategori_manage_list,
        kategori_has_status=kategori_has_is_active_column()
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

    if kategori_has_is_active_column():
        cursor.execute("""
            SELECT id, is_active
            FROM kategori_undangan
            WHERE nama_kategori = %s
        """, (nama_kategori,))
        existing = cursor.fetchone()

        if existing:
            if existing["is_active"] == 1:
                flash("Kategori sudah ada.", "warning")
            else:
                cursor.execute("""
                    UPDATE kategori_undangan
                    SET is_active = 1
                    WHERE id = %s
                """, (existing["id"],))
                conn.commit()
                flash("Kategori berhasil diaktifkan kembali.", "success")
            return redirect(url_for("admin_penerima"))
    else:
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
    nomor_hp = request.form.get("nomor_hp", "").strip()
    kategori_id = request.form.get("kategori_id", "").strip()

    if not nama or not email or not nomor_hp or not kategori_id:
        flash("Nama, email, nomor WhatsApp, dan kategori wajib diisi.", "warning")
        return redirect(url_for("admin_penerima"))
    valid, pesan = validasi_email(email)
    if not valid:
        flash(pesan, "warning")
        return redirect(url_for("admin_penerima"))

    cursor = get_cursor()
    if kategori_has_is_active_column():
        cursor.execute("""
            SELECT id, nama_kategori
            FROM kategori_undangan
            WHERE id = %s AND is_active = 1
        """, (kategori_id,))
    else:
        cursor.execute("""
            SELECT id, nama_kategori
            FROM kategori_undangan
            WHERE id = %s
        """, (kategori_id,))
    kategori = cursor.fetchone()

    if not kategori:
        flash("Kategori tidak valid.", "warning")
        return redirect(url_for("admin_penerima"))

    cursor.execute("""
    INSERT INTO master_peserta_undangan (nama, email, nomor_hp, kategori, kategori_id)
    VALUES (%s, %s, %s, %s, %s)
    """, (nama, email, nomor_hp, kategori["nama_kategori"], kategori["id"]))
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


@app.route("/admin/kategori/nonaktif/<int:id>", methods=["POST"])
def nonaktifkan_kategori(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if not kategori_has_is_active_column():
        flash("Fitur nonaktif kategori belum tersedia di database.", "danger")
        return redirect(url_for("admin_penerima"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT id, nama_kategori, is_active
        FROM kategori_undangan
        WHERE id = %s
    """, (id,))
    kategori = cursor.fetchone()

    if not kategori:
        flash("Kategori tidak ditemukan.", "warning")
        return redirect(url_for("admin_penerima"))

    if kategori["is_active"] == 0:
        flash("Kategori sudah nonaktif.", "info")
        return redirect(url_for("admin_penerima"))

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM master_peserta_undangan
        WHERE kategori_id = %s
    """, (id,))
    pemakaian = cursor.fetchone()

    if pemakaian and pemakaian["total"] > 0:
        flash(
            f"Kategori tidak bisa dinonaktifkan karena masih dipakai {pemakaian['total']} penerima.",
            "warning"
        )
        return redirect(url_for("admin_penerima"))

    cursor.execute("""
        UPDATE kategori_undangan
        SET is_active = 0
        WHERE id = %s
    """, (id,))
    conn.commit()

    flash("Kategori berhasil dinonaktifkan.", "success")
    return redirect(url_for("admin_penerima"))


@app.route("/admin/kategori/hapus/<int:id>", methods=["POST"])
def hapus_kategori(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if not kategori_has_is_active_column():
        flash("Fitur hapus kategori bertahap belum tersedia di database.", "danger")
        return redirect(url_for("admin_penerima"))

    cursor = get_cursor()
    cursor.execute("""
        SELECT id, nama_kategori, is_active
        FROM kategori_undangan
        WHERE id = %s
    """, (id,))
    kategori = cursor.fetchone()

    if not kategori:
        flash("Kategori tidak ditemukan.", "warning")
        return redirect(url_for("admin_penerima"))

    if kategori["is_active"] == 1:
        flash("Kategori aktif tidak bisa dihapus. Nonaktifkan dulu kategori ini.", "warning")
        return redirect(url_for("admin_penerima"))

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM master_peserta_undangan
        WHERE kategori_id = %s
    """, (id,))
    pemakaian = cursor.fetchone()

    if pemakaian and pemakaian["total"] > 0:
        flash(
            f"Kategori tidak bisa dihapus karena masih dipakai {pemakaian['total']} penerima.",
            "warning"
        )
        return redirect(url_for("admin_penerima"))

    cursor.execute("DELETE FROM kategori_undangan WHERE id = %s", (id,))
    conn.commit()

    flash("Kategori berhasil dihapus.", "success")
    return redirect(url_for("admin_penerima"))

# =========================
# DOWNLOAD NOTULENSI
# =========================
@app.route("/download/<filename>")
def download_notulensi(filename):
    return send_from_directory("outputs/notulensi", filename, as_attachment=True)


@app.route("/user/notulensi/preview/<int:id>")
def preview_notulensi(id):
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    cursor = get_cursor()
    
    # Ambil data notulensi dan kegiatannya beserta timestamps
    cursor.execute("""
        SELECT n.id AS notulensi_id, n.file_path, n.ringkasan, n.created_at,
               k.id AS kegiatan_id, k.nama_kegiatan AS kegiatan, k.tempat, k.waktu AS waktu_kegiatan, k.created_by
        FROM notulensi n
        JOIN kegiatan k ON n.kegiatan_id = k.id
        WHERE n.id = %s AND k.created_by = %s
    """, (id, session["user_id"]))
    notulensi = cursor.fetchone()

    if not notulensi:
        flash("Notulensi tidak ditemukan.", "danger")
        return redirect(url_for("riwayat_notulensi"))

    # Format waktu kegiatan (rapat) ke Bahasa Indonesia
    waktu_kegiatan_formatted = "-"
    if notulensi.get("waktu_kegiatan"):
        try:
            waktu_kegiatan_formatted = format_tanggal_indo(notulensi["waktu_kegiatan"]) + " - " + notulensi["waktu_kegiatan"].strftime("%H:%M") + " WIB"
        except Exception:
            waktu_kegiatan_formatted = str(notulensi["waktu_kegiatan"])

    # Format waktu pembuatan notulensi ke Bahasa Indonesia
    waktu_pembuatan_formatted = "-"
    if notulensi.get("created_at"):
        try:
            waktu_pembuatan_formatted = format_tanggal_indo(notulensi["created_at"]) + " - " + notulensi["created_at"].strftime("%H:%M") + " WIB"
        except Exception:
            waktu_pembuatan_formatted = str(notulensi["created_at"])

    # Ambil data nama peserta rapat
    cursor.execute("SELECT nama FROM peserta WHERE kegiatan_id = %s", (notulensi["kegiatan_id"],))
    peserta_rows = cursor.fetchall()
    peserta_list = [p["nama"] for p in peserta_rows]
    peserta_str = ", ".join(peserta_list) if peserta_list else "-"

    # Baca isi file .txt notulensi dari server
    content = ""
    file_path = notulensi["file_path"]
    filename = os.path.basename(file_path.replace("\\", "/")) if file_path else ""
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Gagal membaca isi berkas notulensi: {e}"
    else:
        content = "Berkas notulensi (.txt) tidak ditemukan di server."

    return render_template(
        "user/preview-notulensi.html",
        notulensi=notulensi,
        peserta=peserta_str,
        content=content,
        filename=filename,
        waktu_kegiatan=waktu_kegiatan_formatted,
        waktu_pembuatan=waktu_pembuatan_formatted
    )


@app.route('/kehadiran/<token>', methods=['GET', 'POST'])
def konfirmasi_kehadiran(token):
    # halaman publik untuk mengonfirmasi kehadiran via token
    cursor = get_cursor()
    cursor.execute("""
        SELECT kk.*, u.kegiatan, u.tanggal, u.waktu, u.waktu_selesai, u.tempat
        FROM konfirmasi_kehadiran kk
        LEFT JOIN undangan u ON kk.undangan_id = u.id
        WHERE kk.token = %s
    """, (token,))
    row = cursor.fetchone()

    if not row:
        return render_template('public/kehadiran_selesai.html', message='Token tidak valid atau sudah kadaluwarsa.')

    if request.method == 'GET':
        if row.get('status_kehadiran') is not None:
            return render_template('public/kehadiran_selesai.html', message='Anda sudah melakukan konfirmasi. Terima kasih.')
        return render_template(
            'public/chatbot_kehadiran.html',
            token=token,
            kegiatan=row.get('kegiatan'),
            tanggal_display=format_tanggal_indo(row.get('tanggal')) if row.get('tanggal') else '-',
            waktu_display=format_waktu_rentang(row.get('waktu'), row.get('waktu_selesai'), with_wib=True) if row.get('waktu') else '-',
            tempat=row.get('tempat') or '-'
        )

    # POST: terima data konfirmasi
    data = request.get_json() or request.form
    status_val = data.get('status')
    nama = data.get('nama')
    email = data.get('email')

    if status_val not in ('hadir', 'tidak_hadir', 'diwakilkan'):
        return { 'success': False, 'message': 'Status kehadiran tidak valid.' }, 400

    try:
        cursor.execute("""
            UPDATE konfirmasi_kehadiran
            SET nama = %s,
                email = %s,
                status_kehadiran = %s,
                waktu_konfirmasi = NOW()
            WHERE token = %s
        """, (nama, email, status_val, token))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return { 'success': False, 'message': 'Gagal menyimpan konfirmasi.' }, 500

    return render_template('public/kehadiran_selesai.html', message='Konfirmasi kehadiran berhasil. Terima kasih.')

@app.route("/admin/konfirmasi-manual", methods=["POST"])
def admin_konfirmasi_manual():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    undangan_id = request.form.get("undangan_id")
    nama = request.form.get("nama")
    email = request.form.get("email")
    status_kehadiran = request.form.get("status_kehadiran")
    metode_konfirmasi = request.form.get("metode_konfirmasi")
    catatan = request.form.get("catatan")

    cursor = get_cursor()

    cursor.execute("""
        INSERT INTO konfirmasi_kehadiran
        (undangan_id, nama, email, status_kehadiran, metode_konfirmasi, catatan, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (
        undangan_id,
        nama,
        email,
        status_kehadiran,
        metode_konfirmasi,
        catatan
    ))

    conn.commit()
    flash("Konfirmasi manual berhasil disimpan.", "success")
    return redirect(url_for("admin_monitoring"))


@app.route("/debug-db-status-xyz")
def debug_db_status_xyz():
    cursor = get_cursor()
    cursor.execute("SELECT id, kegiatan, status, tanggal_dibuat, peserta FROM undangan ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    import json
    return json.dumps(rows, default=str)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)