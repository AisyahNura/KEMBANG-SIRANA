import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "kembang_sirana")

SECRET_KEY = os.getenv("SECRET_KEY")

MAIL_SERVER = os.getenv("MAIL_SERVER", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")

FONNTE_TOKEN = os.getenv("FONNTE_TOKEN", "")

UPLOAD_FOLDER = "uploads/audio"
OUTPUT_PDF_FOLDER = "outputs/pdf"
OUTPUT_NOTULENSI_FOLDER = "outputs/notulensi"

TELEGRAM_BOT_TOKEN = "8888340764:AAHSqYsw6Z6VsH9T4V8h8c0KOU1utxG7H1I"
TELEGRAM_CHAT_ID = "6289106550"