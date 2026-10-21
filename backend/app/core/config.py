import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduTrack AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "edutrack-ai-super-secret-key-2026-academico")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite Database URI
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./edutrack.db"
    )
    
    # Optional Gemini AI API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Integração Xano (Google Classroom -> Xano -> EduTrack).
    # Sem valores padrão reais: defina por variável de ambiente (ver .env.example).
    XANO_BASE_URL: str = os.getenv("XANO_BASE_URL", "")
    XANO_API_KEY: str = os.getenv("XANO_API_KEY", "")
    XANO_TIMEOUT_SECONDS: float = float(os.getenv("XANO_TIMEOUT_SECONDS", "15") or "15")
    # A sincronização no Xano percorre a API do Google (paginação) e pode demorar mais.
    XANO_SYNC_TIMEOUT_SECONDS: float = float(os.getenv("XANO_SYNC_TIMEOUT_SECONDS", "60") or "60")
    # URL pública deste app: destino do redirecionamento do Xano após o consentimento do Google.
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")

    class Config:
        case_sensitive = True

settings = Settings()
