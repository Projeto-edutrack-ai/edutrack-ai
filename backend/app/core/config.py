import os
import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduTrack AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(48))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite Database URI
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./edutrack.db"
    )
    
    # Optional Gemini AI API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Xano acadêmico (alunos, materias, tarefas), somente no backend.
    XANO_TIMEOUT_SECONDS: float = 15.0
    XANO_CRUD_BASE_URL: str = os.getenv("XANO_CRUD_BASE_URL", "")
    # URL pública usada nos links de recuperação de senha.
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")

    XANO_CRUD_AUTH_HEADER: str = "Authorization"
    XANO_CRUD_AUTH_VALUE: str = ""
    XANO_PYTHON_BRIDGE_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # E-mail (recuperação de senha). EMAIL_BACKEND: "smtp" envia de verdade; "console" apenas
    # registra no log e grava em outbox/ (modo de desenvolvimento, NÃO entrega e-mail).
    EMAIL_BACKEND: str = os.getenv("EMAIL_BACKEND", "console")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587") or "587")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "EduTrack AI <no-reply@edutrack.local>")
    PASSWORD_RESET_TOKEN_MINUTES: int = int(os.getenv("PASSWORD_RESET_TOKEN_MINUTES", "30") or "30")

    class Config:
        case_sensitive = True

settings = Settings()
