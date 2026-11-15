from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

if engine.dialect.name == 'sqlite':
    from app.core.search_text import search_key

    @event.listens_for(engine, 'connect')
    def register_search_function(dbapi_connection, _connection_record):
        dbapi_connection.create_function('edutrack_search_key', 1, search_key, deterministic=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency para obter sessão do banco de dados em endpoints FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria tabelas ausentes e aplica a migração aditiva (sem apagar dados)."""
    from app.core.migrations import run_migrations
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
