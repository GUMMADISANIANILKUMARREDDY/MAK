import os
from pathlib import Path

from dotenv import load_dotenv

_base_dir = Path(__file__).resolve().parent.parent
load_dotenv(_base_dir / ".env")


def _parse_cors_origins() -> list:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_EXPIRE_DAYS: int = int(os.getenv("REFRESH_EXPIRE_DAYS", "7"))
    # SMTP
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    OTP_EXPIRE_MINUTES: int = 10
    # CORS: comma-separated origins or "*" for all
    CORS_ORIGINS: list = _parse_cors_origins()
    # Rate limit: max requests per window for auth endpoints
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "10"))
    # Storage bucket for task submission files (Supabase)
    STORAGE_BUCKET_SUBMISSIONS: str = os.getenv("STORAGE_BUCKET_SUBMISSIONS", "task-submissions")
    # Cron: optional secret for /cron/deadline-approaching (set in prod for cron job)
    CRON_SECRET: str = os.getenv("CRON_SECRET", "")
    # File upload: max size bytes (default 10MB), allowed extensions
    UPLOAD_MAX_SIZE_MB: int = int(os.getenv("UPLOAD_MAX_SIZE_MB", "10"))
    UPLOAD_ALLOWED_EXTENSIONS: str = os.getenv("UPLOAD_ALLOWED_EXTENSIONS", "pdf,doc,docx,txt,xls,xlsx")


settings = Settings()
