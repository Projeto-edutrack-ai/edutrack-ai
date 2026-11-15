import os
import tempfile

# Isola os testes: banco SQLite temporário (nunca toca em edutrack.db), sem Xano real e sem e-mail real.
# Precisa rodar ANTES de importar qualquer módulo de app.*, pois as configurações são lidas na importação.
_TMP_DIR = tempfile.mkdtemp(prefix="edutrack-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DIR}/test.db"
os.environ["XANO_CRUD_BASE_URL"] = ""
os.environ["EMAIL_BACKEND"] = "console"
os.environ["EMAIL_OUTBOX_DIR"] = os.path.join(_TMP_DIR, "outbox")
os.environ["GEMINI_API_KEY"] = ""

import pytest
from app.core.database import SessionLocal, engine, Base
from seed_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Garante banco de dados (temporário) populado antes de executar os testes."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    engine.dispose()
    import shutil
    shutil.rmtree(_TMP_DIR, ignore_errors=True)
