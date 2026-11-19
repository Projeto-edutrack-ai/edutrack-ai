"""Sincronização do aluno com o Xano (simulado), espelho Xano->SQLite, IA com dados do Xano e
recuperação de senha por e-mail (console e SMTP real em servidor local)."""
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
from aiosmtpd.controller import Controller
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.main import app
from app.models.password_reset import PasswordResetToken
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User
from app.services import email_service, xano_crud
from app.services.xano_crud import XanoCrudClient, mirror_user_data, sync_aluno

client = TestClient(app)


class FakeXano:
    """Xano simulado: tabelas em memória atrás de um httpx.MockTransport."""

    def __init__(self):
        self.tables = {"alunos": [], "materias": [], "tarefas": []}
        self.next_id = 1
        self.fail = False
        self.calls = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path))
        if self.fail:
            return httpx.Response(500, json={"message": "erro interno simulado"})
        table = request.url.path.strip("/").split("/")[-1]
        if request.method == "GET":
            return httpx.Response(200, json=self.tables[table])
        if request.method == "POST":
            import json
            row = {"id": self.next_id, **json.loads(request.content)}
            self.next_id += 1
            self.tables[table].append(row)
            return httpx.Response(200, json=row)
        return httpx.Response(404)

    def client(self) -> XanoCrudClient:
        return XanoCrudClient(base_url="https://xano.test/api:crud", transport=httpx.MockTransport(self.handler))


@pytest.fixture
def fake_xano(monkeypatch):
    fx = FakeXano()
    # Each fake workspace gets a non-overlapping ID range in the shared test database.
    with SessionLocal() as db:
        from sqlalchemy import func
        fx.next_id=(db.query(func.max(User.xano_aluno_id)).scalar() or 0)+1
    monkeypatch.setattr(settings, "XANO_CRUD_BASE_URL", "https://xano.test/api:crud")
    real_init = XanoCrudClient.__init__

    def init(self, base_url=None, timeout=None, transport=None):
        real_init(self, base_url=base_url, timeout=timeout, transport=transport or httpx.MockTransport(fx.handler))

    monkeypatch.setattr(XanoCrudClient, "__init__", init)
    xano_crud._last_mirror.clear()
    return fx


def _register(email, name="Novo Aluno", password="senha-forte-1"):
    return client.post("/api/auth/register", json={"name": name, "email": email, "password": password})


# ---------------------------------------------------------------- aluno no Xano
def test_register_creates_aluno_in_xano(fake_xano):
    resp = _register("novo1@edutrack-qa.com")
    assert resp.status_code == 201
    sync = resp.json()["xano_sync"]
    assert sync["status"] == "synced"
    assert [a["email"] for a in fake_xano.tables["alunos"]] == ["novo1@edutrack-qa.com"]
    assert fake_xano.tables["alunos"][0]["nome"] == "Novo Aluno"
    assert sync["aluno"]["id"] == fake_xano.tables["alunos"][0]["id"]


def test_login_does_not_duplicate_aluno(fake_xano):
    _register("novo2@edutrack-qa.com")
    for _ in range(2):
        r = client.post("/api/auth/login", json={"email": "novo2@edutrack-qa.com", "password": "senha-forte-1"})
        assert r.status_code == 200 and r.json()["xano_sync"]["status"] == "synced"
    assert len(fake_xano.tables["alunos"]) == 1


def test_aluno_is_matched_by_email_not_by_name(fake_xano):
    fake_xano.tables["alunos"].append({"id": 99, "nome": "Mesmo Nome", "email": "outro@x.com"})
    resp = _register("mesmonome@edutrack-qa.com", name="Mesmo Nome")
    assert resp.json()["xano_sync"]["aluno"]["id"] != 99
    assert len(fake_xano.tables["alunos"]) == 2


def test_xano_down_does_not_block_registration_and_reports_failure(fake_xano):
    fake_xano.fail = True
    resp = _register("novo3@edutrack-qa.com")
    assert resp.status_code == 201
    assert resp.json()["xano_sync"]["status"] == "failed"
    assert "500" in resp.json()["xano_sync"]["detail"]
    fake_xano.fail = False
    token = resp.json()["access_token"]
    retry = client.post("/api/auth/xano-sync", headers={"Authorization": f"Bearer {token}"})
    assert retry.json()["status"] == "synced"
    assert len(fake_xano.tables["alunos"]) == 1


def test_sync_skipped_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "XANO_CRUD_BASE_URL", "")
    user = User(id=1, name="x", email="x@x.com")
    assert sync_aluno(user, XanoCrudClient(base_url="")) ["status"] == "skipped"


# ---------------------------------------------------------------- espelho + IA com dados do Xano
def _login_headers(email, password="senha-forte-1"):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_ai_and_analytics_use_data_stored_only_in_xano(fake_xano):
    resp = _register("aluno-ia@edutrack-qa.com")
    aluno_id = resp.json()["xano_sync"]["aluno"]["id"]
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    # antes: sem dados
    first = client.get("/api/ai/insights", headers=headers).json()
    assert "Cadastre suas primeiras disciplinas" in first["summary"]

    past_ms = int((datetime.now(timezone.utc) - timedelta(days=2)).timestamp() * 1000)
    fake_xano.tables["materias"] += [
        {"id": 10, "alunos_id": aluno_id, "nome": "Python", "professor": "Ana", "carga_horaria": 80, "descricao": ""},
        {"id": 11, "alunos_id": 777, "nome": "Matéria de outro aluno", "carga_horaria": 60},
    ]
    fake_xano.tables["tarefas"] += [
        {"id": 20, "materias_id": 10, "titulo_": "Lista 1", "status": "concluida", "prazo": past_ms},
        {"id": 21, "materias_id": 10, "titulo_": "Lista 2", "status": "pendente", "prazo": past_ms},
        {"id": 22, "materias_id": 11, "titulo_": "Tarefa alheia", "status": "pendente", "prazo": None},
    ]
    xano_crud._last_mirror.clear()

    progress = client.get("/api/analytics/progress", headers=headers).json()
    assert progress["total_tasks"] == 2 and progress["completed_tasks"] == 1  # só as do próprio aluno
    xano_crud._last_mirror.clear()
    insights = client.get("/api/ai/insights", headers=headers).json()
    assert "1 de 2 tarefas" in insights["summary"]
    assert any("atrasada" in a for a in insights["critical_alerts"])
    xano_crud._last_mirror.clear()
    answer = client.post("/api/ai/ask", headers=headers, json={"question": "Como está meu tempo e desvio?"})
    assert answer.status_code == 200 and answer.json()["answer"]
    xano_crud._last_mirror.clear()
    pdf = client.get("/api/reports/weekly-pdf", headers=headers)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")


def test_mirror_keeps_local_study_time_and_removes_deleted(fake_xano):
    resp = _register("espelho@edutrack-qa.com")
    aluno_id = resp.json()["xano_sync"]["aluno"]["id"]
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    fake_xano.tables["materias"].append({"id": 30, "alunos_id": aluno_id, "nome": "Redes", "carga_horaria": 60})
    fake_xano.tables["tarefas"].append({"id": 40, "materias_id": 30, "titulo_": "Lab", "status": "pendente"})

    t = client.post("/api/academic_tasks/by-xano/40/study-time", headers=headers, json={"additional_minutes": 25})
    assert t.status_code == 200 and t.json()["actual_time_minutes"] == 25
    t = client.post("/api/academic_tasks/by-xano/40/study-time", headers=headers, json={"additional_minutes": 5})
    assert t.json()["actual_time_minutes"] == 30  # sem duplicar a tarefa, tempo acumulado

    fake_xano.tables["tarefas"][0]["titulo_"] = "Lab 2"
    xano_crud._last_mirror.clear()
    client.get("/api/analytics/progress", headers=headers)
    db = SessionLocal()
    try:
        tasks = db.query(AcademicTask).filter(AcademicTask.xano_id == 40).all()
        assert len(tasks) == 1 and tasks[0].title == "Lab 2" and tasks[0].actual_time_minutes == 30
        fake_xano.tables["tarefas"].clear()
        xano_crud._last_mirror.clear()
        client.get("/api/analytics/progress", headers=headers)
        db.expire_all()
        assert db.query(AcademicTask).filter(AcademicTask.xano_id == 40).count() == 0
    finally:
        db.close()


def test_xano_outage_keeps_analytics_working(fake_xano):
    resp = _register("offline@edutrack-qa.com")
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    fake_xano.fail = True
    xano_crud._last_mirror.clear()
    assert client.get("/api/analytics/progress", headers=headers).status_code == 502


def test_ask_assistant_time_question_regression():
    """Antes: AttributeError (total_time_spent_hours) nas perguntas sobre tempo/desvio."""
    h = _login_headers_demo()
    for q in ("Qual meu desvio de tempo?", "Como organizar meu cronograma da semana?", "Oi"):
        r = client.post("/api/ai/ask", headers=h, json={"question": q})
        assert r.status_code == 200, q


def _login_headers_demo():
    r = client.post("/api/auth/login", json={"email": "aluno@edutrack.edu.br", "password": "senha123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ---------------------------------------------------------------- recuperação de senha
def _latest_link(outbox: Path) -> str:
    files = sorted(outbox.glob("*.eml"))
    assert files, "nenhum e-mail gravado"
    body = files[-1].read_text()
    return re.search(r"reset_token=([A-Za-z0-9_\-]+)", body).group(1)


def test_forgot_password_sends_email_and_reset_works_once(monkeypatch, tmp_path):
    monkeypatch.setattr(email_service, "OUTBOX_DIR", tmp_path)
    _register("reset1@edutrack-qa.com", password="antiga-senha")
    resp = client.post("/api/auth/forgot-password", json={"email": "reset1@edutrack-qa.com"})
    assert resp.status_code == 200
    token = _latest_link(tmp_path)

    bad = client.post("/api/auth/reset-password", json={"token": "token-errado", "new_password": "nova-senha-1"})
    assert bad.status_code == 400
    short = client.post("/api/auth/reset-password", json={"token": token, "new_password": "123"})
    assert short.status_code == 400

    ok = client.post("/api/auth/reset-password", json={"token": token, "new_password": "nova-senha-1"})
    assert ok.status_code == 200
    assert client.post("/api/auth/login", json={"email": "reset1@edutrack-qa.com", "password": "antiga-senha"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "reset1@edutrack-qa.com", "password": "nova-senha-1"}).status_code == 200

    reuse = client.post("/api/auth/reset-password", json={"token": token, "new_password": "outra-senha-2"})
    assert reuse.status_code == 400  # uso único


def test_unknown_email_sends_nothing(monkeypatch, tmp_path):
    monkeypatch.setattr(email_service, "OUTBOX_DIR", tmp_path)
    client.post("/api/auth/forgot-password", json={"email": "fantasma@edutrack-qa.com"})
    assert list(tmp_path.glob("*.eml")) == []


def test_expired_and_superseded_tokens_are_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(email_service, "OUTBOX_DIR", tmp_path)
    _register("reset2@edutrack-qa.com")
    client.post("/api/auth/forgot-password", json={"email": "reset2@edutrack-qa.com"})
    first = _latest_link(tmp_path)
    time.sleep(0.01)
    client.post("/api/auth/forgot-password", json={"email": "reset2@edutrack-qa.com"})
    second = _latest_link(tmp_path)
    assert first != second
    assert client.post("/api/auth/reset-password", json={"token": first, "new_password": "abcdef1"}).status_code == 400

    db = SessionLocal()
    try:
        rec = db.query(PasswordResetToken).filter(PasswordResetToken.used_at.is_(None)).order_by(PasswordResetToken.id.desc()).first()
        rec.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()
    assert client.post("/api/auth/reset-password", json={"token": second, "new_password": "abcdef1"}).status_code == 400


def test_reset_email_really_goes_through_smtp(monkeypatch):
    """Sobe um servidor SMTP real em localhost e confere que a mensagem é entregue a ele."""
    received = []

    class Handler:
        async def handle_DATA(self, server, session, envelope):
            received.append(envelope)
            return "250 OK"

    import socket
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    controller = Controller(Handler(), hostname="127.0.0.1", port=port)
    controller.start()
    try:
        monkeypatch.setattr(settings, "EMAIL_BACKEND", "smtp")
        monkeypatch.setattr(settings, "SMTP_HOST", "127.0.0.1")
        monkeypatch.setattr(settings, "SMTP_PORT", port)
        monkeypatch.setattr(settings, "SMTP_USE_TLS", False)
        monkeypatch.setattr(settings, "SMTP_USER", "")
        _register("smtp@edutrack-qa.com")
        resp = client.post("/api/auth/forgot-password", json={"email": "smtp@edutrack-qa.com"})
        assert resp.status_code == 200 and resp.json()["email_backend"] == "smtp"
    finally:
        controller.stop()
    assert len(received) == 1
    assert received[0].rcpt_tos == ["smtp@edutrack-qa.com"]
    content = received[0].content.decode()
    assert "reset_token=" in content and "Redefini" in content


def test_smtp_failure_does_not_leak_or_crash(monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_BACKEND", "smtp")
    monkeypatch.setattr(settings, "SMTP_HOST", "127.0.0.1")
    monkeypatch.setattr(settings, "SMTP_PORT", 1)  # nada escutando
    monkeypatch.setattr(settings, "SMTP_USE_TLS", False)
    _register("smtpfail@edutrack-qa.com")
    ok = client.post("/api/auth/forgot-password", json={"email": "smtpfail@edutrack-qa.com"})
    unknown = client.post("/api/auth/forgot-password", json={"email": "nada@edutrack-qa.com"})
    assert ok.status_code == unknown.status_code == 200 and ok.json() == unknown.json()
