from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.services.xano_crud import XanoCrudClient,XanoCrudError
from test_adequacao import register
from test_xano_sync_and_reset import fake_xano

client=TestClient(app)


def test_binding_is_not_reused_for_another_workspace(fake_xano,monkeypatch):
    headers,user=register()
    monkeypatch.setattr(settings,'XANO_CRUD_BASE_URL','https://another-workspace.test')
    result=client.post('/api/auth/xano-sync',headers=headers)
    assert result.json()['status']=='link_required'
    assert client.get('/api/xano/materias',headers=headers).status_code==502


def test_direct_network_client_refuses_missing_service_credential(monkeypatch):
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_VALUE','')
    api=XanoCrudClient(base_url='https://example.test')
    with pytest.raises(XanoCrudError,match='credencial'):
        api._request('GET','/alunos')


def test_classroom_columns_are_preserved_without_active_integration():
    # Compatibility metadata is preserved; this is not a reintroduction of integration code.
    from app.models.subject import Subject
    from app.models.task import AcademicTask
    assert 'classroom_course_id' in Subject.__table__.columns
    assert 'classroom_coursework_id' in AcademicTask.__table__.columns
    assert not (Path(__file__).parents[1]/'backend/app/api/classroom.py').exists()


def test_remote_subject_payload_rejects_blank_or_null_required_fields():
    headers,_=register()
    assert client.post('/api/xano/materias',headers=headers,json={'nome':'   '}).status_code==422
    row=client.post('/api/xano/materias',headers=headers,json={'nome':'Válida'}).json()
    assert client.patch(f"/api/xano/materias/{row['id']}",headers=headers,json={'nome':None}).status_code==422
