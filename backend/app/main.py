import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Garante registro dos modelos no Base

# Importação dos Roteadores
from app.api.auth import router as auth_router
from app.api.subjects import router as subjects_router
from app.api.tasks import router as tasks_router
from app.api.analytics import router as analytics_router
from app.api.ai_insights import router as ai_router
from app.api.reports import router as reports_router
from app.api.search import router as search_router

# Criação automática de tabelas SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EduTrack AI — API Backend Inteligente",
    description=(
        "Backend de alta performance para o Assistente Educacional Personalizado EduTrack AI. "
        "Construído segundo a metodologia Spec-Driven Development (OpenSpec) e especificação canônica do curso."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir acesso local e Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das Rotas
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(subjects_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)

# Servir Frontend Estático se existir
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return RedirectResponse(url="/docs")
else:
    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")
