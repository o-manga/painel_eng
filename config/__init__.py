import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def settings():
    load_dotenv(ROOT / ".env")
    configured = os.getenv("DATABASE_PATH")
    database = Path(configured).expanduser() if configured else ROOT / "instance" / "engenharia.sqlite3"
    if not database.is_absolute():
        database = ROOT / database
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY") or secrets.token_hex(32),
        "DATABASE": str(database),
        "PORT": int(os.getenv("PORT") or 5000),
        "MAX_CONTENT_LENGTH": 128 * 1024,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
    }
