import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_demo_user():
    response = client.post("/api/auth/login", json={
        "email": "aluno@edutrack.edu.br",
        "password": "senha123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "aluno@edutrack.edu.br"
    # Verifica os novos campos de perfil acadêmico
    assert "course" in data["user"]
    assert "college_year" in data["user"]

def test_swagger_oauth_token_authenticates_protected_routes():
    response = client.post("/api/auth/token", data={
        "username": "aluno@edutrack.edu.br",
        "password": "senha123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    profile = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["email"] == "aluno@edutrack.edu.br"

def test_unauthorized_access_subjects():
    response = client.get("/api/subjects")
    assert response.status_code == 401

def test_update_user_profile():
    """Testa a edição de perfil: nome, foto, curso, ano letivo e faculdade."""
    login_resp = client.post("/api/auth/login", json={
        "email": "aluno@edutrack.edu.br",
        "password": "senha123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_resp = client.put("/api/auth/profile", json={
        "name": "Lucas Atualizado",
        "course": "Engenharia de Software",
        "college_year": "4º Ano / 8º Semestre",
        "institution": "Universidade Estadual de Tecnologia",
        "bio": "Foco em Machine Learning e DevOps."
    }, headers=headers)

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "Lucas Atualizado"
    assert data["course"] == "Engenharia de Software"
    assert data["college_year"] == "4º Ano / 8º Semestre"

def test_login_and_get_analytics():
    login_resp = client.post("/api/auth/login", json={
        "email": "aluno@edutrack.edu.br",
        "password": "senha123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Testar endpoint de progresso
    analytics_resp = client.get("/api/analytics/progress", headers=headers)
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert "overall_weighted_progress" in data
    assert "study_velocity_tasks_per_week" in data

    # Testar endpoint de IA
    ai_resp = client.get("/api/ai/insights", headers=headers)
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()
    assert "summary" in ai_data
    assert "recommendations" in ai_data

    # Testar download de PDF
    pdf_resp = client.get("/api/reports/weekly-pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"

def test_forgot_password_never_reveals_whether_email_exists():
    known = client.post("/api/auth/forgot-password", json={"email": "aluno@edutrack.edu.br"})
    unknown = client.post("/api/auth/forgot-password", json={"email": "ninguem@nao-existe.com"})
    assert known.status_code == unknown.status_code == 200
    assert known.json()["message"] == unknown.json()["message"]
    assert "aluno@edutrack.edu.br" not in known.json()["message"]

def test_ai_assistant_ask():
    login_resp = client.post("/api/auth/login", json={
        "email": "aluno@edutrack.edu.br",
        "password": "senha123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    ask_resp = client.post("/api/ai/ask", headers=headers, json={
        "question": "Como devo priorizar minhas tarefas hoje?"
    })
    assert ask_resp.status_code == 200
    data = ask_resp.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
    assert "source" in data
