import pytest
from app.core.database import SessionLocal, engine, Base
from seed_data import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Garante banco de dados populado antes de executar os testes."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
