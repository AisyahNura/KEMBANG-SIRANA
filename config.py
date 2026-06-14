import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "kembang_sirana")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

MAIL_SERVER = os.getenv("MAIL_SERVER", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")

FONNTE_TOKEN = os.getenv("FONNTE_TOKEN", "")

UPLOAD_FOLDER = "uploads/audio"
OUTPUT_PDF_FOLDER = "outputs/pdf"
OUTPUT_NOTULENSI_FOLDER = "outputs/notulensi"

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
FONNTE_TOKEN = "tMBb8detcMKKmcAnd5tW"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

