"""Testes das rotas /api/classroom com Xano mockado (sem credenciais reais, sem rede)."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import classroom as classroom_api
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User
from app.services.classroom_sync import ClassroomSyncError
from app.services.xano_client import XanoClient
from classroom_fakes import FakeXano
from classroom_helpers import make_course, make_export, make_work

PREFIX = "/api/classroom"


@pytest.fixture()
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    ana = User(name="Ana", email="ana@x.com", password_hash="h")
    bruno = User(name="Bruno", email="bruno@x.com", password_hash="h")
    db.add_all([ana, bruno])
    db.commit()
    fake = FakeXano()
    holder = {"user": ana, "client": fake.client()}

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: holder["user"]
    app.dependency_overrides[classroom_api.get_xano_client] = lambda: holder["client"]
    try:
        yield {"http": TestClient(app), "db": db, "ana": ana, "bruno": bruno, "fake": fake, "holder": holder}
    finally:
        app.dependency_overrides.clear()
        db.close()
        engine.dispose()


def seed_export(env, user, courses):
    env["fake"].exports[user.id] = make_export(user.id, courses)


def paths(fake):
    return [c.url.path.rsplit("/", 2)[-2] + "/" + c.url.path.rsplit("/", 1)[-1] for c in fake.calls]


# ----------------------------------------------------------------------------- autenticação

def test_rotas_exigem_login():
    client = TestClient(app)  # sem overrides de autenticação
    for method, path in (("get", "/status"), ("post", "/connect"), ("post", "/sync"), ("get", "/courses"),
                         ("get", "/tasks"), ("delete", "/connection"), ("get", "/courses/remote")):
        assert getattr(client, method)(PREFIX + path).status_code == 401


# ----------------------------------------------------------------------------- status

def test_status_sem_xano_configurado(env):
    env["holder"]["client"] = XanoClient(base_url="", api_key="")
    body = env["http"].get(f"{PREFIX}/status").json()
    assert (body["configured"], body["reachable"], body["connected"], body["status"]) == (False, False, False, "not_configured")
    assert env["fake"].calls == []


def test_status_nao_conectado_e_conectado(env):
    http, fake, ana = env["http"], env["fake"], env["ana"]
    body = http.get(f"{PREFIX}/status").json()
    assert (body["configured"], body["reachable"], body["connected"], body["status"]) == (True, True, False, "not_connected")

    fake.statuses[ana.id] = {"connected": True, "status": "active", "google_email": "ana@gmail.com",
                             "last_sync_at": "2026-10-01T12:00:00Z"}
    body = http.get(f"{PREFIX}/status").json()
    assert (body["connected"], body["status"], body["google_email"]) == (True, "active", "ana@gmail.com")
    assert body["last_sync_at"].startswith("2026-10-01T12:00:00")
    assert fake.calls[-1].url.params["local_user_id"] == str(ana.id)


def test_status_tolera_dados_invalidos_e_xano_fora_do_ar(env):
    http, fake, ana = env["http"], env["fake"], env["ana"]
    fake.statuses[ana.id] = {"connected": "sim", "status": 5, "google_email": 7, "last_sync_at": "ontem"}
    body = http.get(f"{PREFIX}/status").json()
    assert (body["connected"], body["status"], body["google_email"], body["last_sync_at"]) == (False, "not_connected", None, None)
    for mode in ("500", "timeout", "connect", "not_json"):
        fake.mode = mode
        response = http.get(f"{PREFIX}/status")
        assert response.status_code == 200 and response.json()["status"] == "unreachable"


# ----------------------------------------------------------------------------- connect / disconnect

def test_connect_devolve_url_do_google_via_xano(env):
    response = env["http"].post(f"{PREFIX}/connect")
    assert response.status_code == 200 and response.json() == {"authorization_url": FakeXano.AUTH_URL}
    request = env["fake"].calls[0]
    assert request.url.path.endswith("/oauth/google/start")
    import json
    assert json.loads(request.content) == {"local_user_id": env["ana"].id,
                                           "return_url": settings.APP_BASE_URL.rstrip("/") + "/"}


def test_connect_rejeita_url_insegura_e_erros_do_xano(env):
    env["fake"].mode = "no_auth_url"
    assert env["http"].post(f"{PREFIX}/connect").status_code == 502
    env["fake"].mode = "500"
    assert env["http"].post(f"{PREFIX}/connect").status_code == 502
    env["holder"]["client"] = XanoClient(base_url="", api_key="")
    assert env["http"].post(f"{PREFIX}/connect").status_code == 503


def test_disconnect_mantem_dados_locais(env):
    seed_export(env, env["ana"], [make_course()])
    env["http"].post(f"{PREFIX}/sync")
    response = env["http"].delete(f"{PREFIX}/connection")
    assert response.status_code == 200 and response.json()["disconnected"] is True
    assert env["fake"].disconnected == [env["ana"].id]
    assert env["db"].query(Subject).count() == 1 and env["db"].query(AcademicTask).count() == 1


# ----------------------------------------------------------------------------- sync

def test_sync_importa_e_e_idempotente(env):
    http, db, fake, ana = env["http"], env["db"], env["fake"], env["ana"]
    seed_export(env, ana, [make_course("C1", "Cálculo I", [make_work("W1"), make_work("W2", "Prova", max_points=5)])])

    first = http.post(f"{PREFIX}/sync")
    assert first.status_code == 200
    body = first.json()
    assert body["remote"]["status"] == "success"
    assert (body["result"]["courses_created"], body["result"]["tasks_created"]) == (1, 2)

    second = http.post(f"{PREFIX}/sync").json()
    assert (second["result"]["courses_created"], second["result"]["tasks_created"]) == (0, 0)
    assert (db.query(Subject).count(), db.query(AcademicTask).count()) == (1, 2)
    assert any(p.endswith("classroom/sync") for p in paths(fake))


def test_sync_sem_refresh_nao_chama_o_google_via_xano(env):
    seed_export(env, env["ana"], [make_course()])
    response = env["http"].post(f"{PREFIX}/sync", json={"refresh": False})
    assert response.status_code == 200 and response.json()["remote"] is None
    assert not any(p.endswith("classroom/sync") for p in paths(env["fake"]))
    assert env["db"].query(AcademicTask).count() == 1


def test_sync_erros_do_xano_viram_http_seguro_e_nao_alteram_o_banco(env):
    seed_export(env, env["ana"], [make_course()])
    for mode, expected in (("409", 409), ("500", 502), ("401", 502), ("timeout", 504), ("connect", 502),
                           ("not_json", 502), ("list", 502)):
        env["fake"].mode = mode
        response = env["http"].post(f"{PREFIX}/sync")
        assert response.status_code == expected, mode
        assert "test-key-not-real" not in response.text
    assert env["db"].query(Subject).count() == 0
    env["holder"]["client"] = XanoClient(base_url="", api_key="")
    assert env["http"].post(f"{PREFIX}/sync").status_code == 503


def test_sync_falha_de_banco_devolve_500_generico(env, monkeypatch):
    seed_export(env, env["ana"], [make_course()])

    def boom(*args, **kwargs):
        raise ClassroomSyncError("detalhe interno")
    monkeypatch.setattr(classroom_api, "sync_user_from_xano", boom)
    response = env["http"].post(f"{PREFIX}/sync")
    assert response.status_code == 500 and "detalhe interno" not in response.text


def test_sync_simultanea_do_mesmo_usuario_e_bloqueada(env):
    lock = classroom_api._lock_for(env["ana"].id)
    assert lock.acquire(blocking=False)
    try:
        assert env["http"].post(f"{PREFIX}/sync").status_code == 409
    finally:
        lock.release()
    seed_export(env, env["ana"], [make_course()])
    assert env["http"].post(f"{PREFIX}/sync").status_code == 200  # lock liberado após o término


# ----------------------------------------------------------------------------- leitura (formato do frontend)

def test_cursos_e_atividades_no_formato_do_frontend(env):
    http, db, ana = env["http"], env["db"], env["ana"]
    db.add(Subject(user_id=ana.id, name="Disciplina local"))  # não deve aparecer nas rotas do Classroom
    db.commit()
    seed_export(env, ana, [
        make_course("C1", "Cálculo I", [
            make_work("W1", "Lista 1", due_at="2026-10-20T12:00:00Z", max_points=10),
            make_work("W2", "Prova", due_at="2026-10-10T12:00:00Z", submission={"state": "TURNED_IN"}),
            make_work("W3", "Sem prazo", due_at=None, max_points=None, alternate_link=None),
        ]),
        make_course("C2", "Álgebra", []),
    ])
    http.post(f"{PREFIX}/sync")

    courses = http.get(f"{PREFIX}/courses").json()
    assert {c["name"] for c in courses} == {"Cálculo I", "Álgebra"}
    calc = next(c for c in courses if c["classroom_course_id"] == "C1")
    assert (calc["tasks_total"], calc["tasks_pending"]) == (3, 2) and calc["link"].endswith("/c/C1")
    assert next(c for c in courses if c["classroom_course_id"] == "C2")["tasks_total"] == 0

    tasks = http.get(f"{PREFIX}/tasks").json()
    assert [t["title"] for t in tasks] == ["Prova", "Lista 1", "Sem prazo"]  # prazo mais próximo primeiro, sem prazo no fim
    lista = tasks[1]
    assert lista["course_name"] == "Cálculo I" and lista["max_points"] == 10.0 and lista["status"] == "pending"
    assert lista["classroom_coursework_id"] == "W1" and lista["link"].endswith("/w/W1")
    assert lista["due_date"].startswith("2026-10-20T12:00:00")
    assert tasks[0]["status"] == "completed" and tasks[0]["submission_state"] == "TURNED_IN"
    assert tasks[2]["due_date"] is None and tasks[2]["max_points"] is None and tasks[2]["link"] is None

    assert [t["title"] for t in http.get(f"{PREFIX}/tasks", params={"status": "completed"}).json()] == ["Prova"]
    calc_id = calc["id"]
    assert len(http.get(f"{PREFIX}/tasks", params={"course_id": calc_id}).json()) == 3
    assert http.get(f"{PREFIX}/tasks", params={"limit": 1}).json()[0]["title"] == "Prova"
    assert http.get(f"{PREFIX}/tasks", params={"limit": 0}).status_code == 422


def test_isolamento_entre_usuarios_nas_rotas(env):
    http, holder, ana, bruno = env["http"], env["holder"], env["ana"], env["bruno"]
    seed_export(env, ana, [make_course("C1", "Curso da Ana", [make_work("W1", "Tarefa da Ana")])])
    seed_export(env, bruno, [make_course("C1", "Curso do Bruno", [make_work("W1", "Tarefa do Bruno")])])
    http.post(f"{PREFIX}/sync")
    holder["user"] = bruno
    http.post(f"{PREFIX}/sync")

    assert [c["name"] for c in http.get(f"{PREFIX}/courses").json()] == ["Curso do Bruno"]
    assert [t["title"] for t in http.get(f"{PREFIX}/tasks").json()] == ["Tarefa do Bruno"]
    holder["user"] = ana
    assert [c["name"] for c in http.get(f"{PREFIX}/courses").json()] == ["Curso da Ana"]
    ana_course_id = http.get(f"{PREFIX}/courses").json()[0]["id"]
    holder["user"] = bruno
    assert http.get(f"{PREFIX}/tasks", params={"course_id": ana_course_id}).json() == []  # não enxerga curso alheio
    body = http.get(f"{PREFIX}/status").json()
    assert body["local"]["courses"] == 1 and body["local"]["tasks"] == 1


def test_cursos_remotos(env):
    env["fake"].courses[env["ana"].id] = [
        {"google_course_id": "C1", "name": "Cálculo", "selected": True, "is_active": True, "token": "segredo"},
        {"google_course_id": "", "name": "sem id"},
        {"google_course_id": 77, "name": None, "selected": "talvez"},
    ]
    body = env["http"].get(f"{PREFIX}/courses/remote").json()
    assert [c["google_course_id"] for c in body] == ["C1", "77"]
    assert "token" not in body[0] and body[1]["selected"] is None
    env["fake"].mode = "500"
    assert env["http"].get(f"{PREFIX}/courses/remote").status_code == 502


def test_preserva_campos_locais_via_api(env):
    http, db, ana = env["http"], env["db"], env["ana"]
    seed_export(env, ana, [make_course()])
    http.post(f"{PREFIX}/sync")
    task = db.query(AcademicTask).one()
    task.actual_time_minutes, task.status = 33.0, "in_progress"
    db.query(Subject).one().workload_hours = 99.0
    db.commit()
    seed_export(env, ana, [make_course(coursework=[make_work(title="Título novo", max_points=3)])])
    http.post(f"{PREFIX}/sync")
    task = db.query(AcademicTask).one()
    assert (task.title, task.max_points, task.actual_time_minutes, task.status) == ("Título novo", 3.0, 33.0, "in_progress")
    assert db.query(Subject).one().workload_hours == 99.0
