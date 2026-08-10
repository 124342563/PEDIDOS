import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "tgc-logistica-secret-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.sqlite')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads")
    )
    EXPORT_FOLDER = os.environ.get(
        "EXPORT_FOLDER", os.path.join(BASE_DIR, "exports")
    )
    REMISIONES_FOLDER = os.environ.get(
        "REMISIONES_FOLDER", os.path.join(BASE_DIR, "remisiones")
    )
    BACKUP_FOLDER = os.environ.get(
        "BACKUP_FOLDER", os.path.join(BASE_DIR, "backups")
    )
    LOG_FOLDER = os.environ.get(
        "LOG_FOLDER", os.path.join(BASE_DIR, "logs")
    )

    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zoho.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "")

    SIMPLIROUTE_TOKEN = os.environ.get("SIMPLIROUTE_TOKEN", "")
    ALAS_API_URL = os.environ.get("ALAS_API_URL", "")
    ALAS_API_KEY = os.environ.get("ALAS_API_KEY", "")
    PIBOX_API_KEY = os.environ.get("PIBOX_API_KEY", "")

    WHATSAPP_MODE = os.environ.get("WHATSAPP_MODE", "WEB_LINK")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
