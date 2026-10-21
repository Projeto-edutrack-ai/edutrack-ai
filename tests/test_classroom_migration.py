"""Testes da migração aditiva do SQLite (preserva dados; idempotente)."""
import sqlite3

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.migrations import plan_migration, run_migrations
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User

# DDL do esquema ANTERIOR à integração (copiado do edutrack.db original do projeto)
OLD_SCHEMA = """
CREATE TABLE users (id INTEGER NOT NULL, name VARCHAR NOT NULL, email VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL, avatar_url TEXT, course VARCHAR, college_year VARCHAR,
  institution VARCHAR, bio VARCHAR, created_at DATETIME, PRIMARY KEY (id));
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE TABLE subjects (id INTEGER NOT NULL, user_id INTEGER NOT NULL, name VARCHAR NOT NULL,
  professor VARCHAR, workload_hours FLOAT NOT NULL, description VARCHAR, start_date DATETIME,
  end_date DATETIME, created_at DATETIME, PRIMARY KEY (id),
  FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE);
CREATE TABLE academic_tasks (id INTEGER NOT NULL, user_id INTEGER NOT NULL, subject_id INTEGER NOT NULL,
  title VARCHAR NOT NULL, description VARCHAR, due_date DATETIME, status VARCHAR NOT NULL,
  estimated_time_minutes FLOAT NOT NULL, actual_time_minutes FLOAT NOT NULL, completed_at DATETIME,
  created_at DATETIME, PRIMARY KEY (id),
  FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY(subject_id) REFERENCES subjects (id) ON DELETE CASCADE);
INSERT INTO users (id, name, email, password_hash) VALUES (1, 'Lucas', 'l@x.com', 'h');
INSERT INTO subjects (id, user_id, name, professor, workload_hours) VALUES (1, 1, 'Física', 'Prof. A', 80);
INSERT INTO academic_tasks (id, user_id, subject_id, title, status, estimated_time_minutes, actual_time_minutes)
  VALUES (1, 1, 1, 'Lista', 'in_progress', 90, 45);
"""


def _old_db(tmp_path):
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.executescript(OLD_SCHEMA)
    conn.commit()
    conn.close()
    return create_engine(f"sqlite:///{path}")


def test_migra_banco_antigo_preservando_dados(tmp_path):
    engine = _old_db(tmp_path)
    executed = run_migrations(engine)
    assert executed  # houve algo a fazer

    cols = {t: {c["name"] for c in inspect(engine).get_columns(t)} for t in ("subjects", "academic_tasks")}
    assert {"source", "classroom_course_id", "classroom_link", "classroom_synced_at"} <= cols["subjects"]
    assert {"source", "classroom_coursework_id", "classroom_link", "max_points",
            "classroom_submission_state", "classroom_synced_at"} <= cols["academic_tasks"]
    index_names = {i["name"] for t in ("subjects", "academic_tasks") for i in inspect(engine).get_indexes(t)}
    assert {"uq_subjects_user_classroom_course", "uq_tasks_user_subject_coursework"} <= index_names

    with engine.connect() as conn:
        subject = conn.execute(text("SELECT name, professor, workload_hours, source FROM subjects")).one()
        task = conn.execute(text(
            "SELECT title, status, estimated_time_minutes, actual_time_minutes, source FROM academic_tasks")).one()
    assert tuple(subject) == ("Física", "Prof. A", 80.0, "local")
    assert tuple(task) == ("Lista", "in_progress", 90.0, 45.0, "local")


def test_migracao_e_idempotente(tmp_path):
    engine = _old_db(tmp_path)
    assert run_migrations(engine)
    assert run_migrations(engine) == []
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM subjects")).scalar() == 1


def test_banco_antigo_migrado_aceita_os_modelos_novos(tmp_path):
    engine = _old_db(tmp_path)
    run_migrations(engine)
    db = sessionmaker(bind=engine)()
    try:
        old = db.query(Subject).filter_by(id=1).one()
        assert old.source == "local" and old.classroom_course_id is None
        subject = Subject(user_id=1, name="Cálculo", source="classroom", classroom_course_id="C1")
        db.add(subject)
        db.flush()
        db.add(AcademicTask(user_id=1, subject_id=subject.id, title="T", source="classroom",
                            classroom_coursework_id="W1", max_points=10.0))
        db.commit()
        assert db.query(AcademicTask).count() == 2
    finally:
        db.close()


def test_banco_novo_nao_precisa_de_migracao(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'new.db'}")
    Base.metadata.create_all(bind=engine)
    assert run_migrations(engine) == []


def test_plan_migration_ignora_tabelas_ausentes_e_so_adiciona_o_que_falta():
    assert plan_migration({}, []) == []
    partial = {"subjects": ["id", "user_id", "source", "classroom_course_id", "classroom_link", "classroom_synced_at"]}
    statements = plan_migration(partial, [])
    assert statements == [
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_subjects_user_classroom_course ON subjects (user_id, classroom_course_id)"
    ]
    assert all(not s.upper().startswith(("DROP", "DELETE", "UPDATE")) for s in plan_migration(
        {"subjects": ["id"], "academic_tasks": ["id"]}, []))
