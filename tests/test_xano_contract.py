"""Contract-shaped fake based on the user's OpenAPI; never calls the real Xano."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
import httpx
import pytest
from app.main import app
from app.core.config import settings
from app.services.xano_crud import XanoCrudClient,_last_mirror
from app.models.user import User
from app.core.database import SessionLocal
from test_adequacao import register

client=TestClient(app)
CONTRACT=json.loads((Path(__file__).parent/'fixtures/xano-contract.json').read_text())


@pytest.fixture
def contract_server(monkeypatch):
    tables={name:[] for name in CONTRACT['fields']}
    with SessionLocal() as db:
        from sqlalchemy import func
        first=(db.query(func.max(User.xano_aluno_id)).scalar() or 0)+10000
    state={'next':first,'calls':[]}
    def handle(request):
        method=request.method
        parts=request.url.path.strip('/').split('/')
        table=parts[0]
        if table not in tables:return httpx.Response(404,json={})
        item_id=int(parts[1]) if len(parts)>1 else None
        payload=json.loads(request.content) if request.content else {}
        assert request.headers['X-Backend-Key']=='unit-test-secret'
        state['calls'].append((method,table,item_id,payload))
        for key,value in payload.items():
            assert key in CONTRACT['fields'][table], f'Undocumented field {key}'
            kind=CONTRACT['fields'][table][key]
            if value is None:
                assert table=='tarefas' and key=='prazo'
            elif kind=='integer':assert type(value) is int
            elif kind=='number':assert type(value) in (int,float)
            else:assert isinstance(value,str)
        if table=='tarefas' and 'status' in payload:
            assert payload['status'] in CONTRACT['status_enum']
        if method=='GET':
            if item_id is None:return httpx.Response(200,json=tables[table])
            row=next((x for x in tables[table] if x['id']==item_id),None)
            return httpx.Response(200 if row else 404,json=row or {})
        if method=='POST':
            state['next']+=1
            row={'id':state['next'],'created_at':1794300000000,**payload}
            tables[table].append(row)
            return httpx.Response(200,json=row)
        row=next((x for x in tables[table] if x['id']==item_id),None)
        if row is None:return httpx.Response(404,json={})
        if method=='PATCH':
            row.update(payload);return httpx.Response(200,json=row)
        if method=='DELETE':
            tables[table].remove(row);return httpx.Response(200,content=b'null',headers={'content-type':'application/json'})
        return httpx.Response(405,json={})
    monkeypatch.setattr(settings,'XANO_CRUD_BASE_URL','https://contract.test')
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_HEADER','X-Backend-Key')
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_VALUE','unit-test-secret')
    original=XanoCrudClient.__init__
    def init(self,base_url=None,timeout=None,transport=None):
        original(self,base_url,timeout,transport or httpx.MockTransport(handle))
    monkeypatch.setattr(XanoCrudClient,'__init__',init)
    _last_mirror.clear()
    return tables,state


def test_remote_crud_search_progress_report_and_timer_match_supplied_contract(contract_server):
    tables,state=contract_server
    headers,user=register()
    subject=client.post('/api/xano/materias',headers=headers,json={
        'nome':'Python contrato','professor':'Ana','descricao':'Teste','carga_horaria':80})
    assert subject.status_code==201,subject.text
    sid=subject.json()['id']
    task=client.post('/api/xano/tarefas',headers=headers,json={
        'materias_id':sid,'titulo_':'Lista contrato','descricao':'Teste','prazo':1577836800000,
        'status':'em_andamento','estimated_time_minutes':90,'actual_time_minutes':0})
    assert task.status_code==201,task.text
    tid=task.json()['id']
    assert tables['tarefas'][0]['status']=='em_andamento '
    assert task.json()['estimated_time_minutes']==90
    # UI-only metadata must never be sent to Xano's documented input schema.
    assert 'estimated_time_minutes' not in tables['tarefas'][0]
    result=client.get('/api/search?overdue=true',headers=headers)
    assert result.status_code==200 and result.json()['subjects'][0]['name']=='Python contrato'
    timer=client.post(f'/api/academic_tasks/by-xano/{tid}/study-time',headers=headers,
                      json={'additional_minutes':12,'new_status':'completed'})
    assert timer.status_code==200,timer.text
    assert timer.json()['actual_time_minutes']==12
    assert tables['tarefas'][0]['status']=='concluida'
    result=client.get('/api/analytics/progress',headers=headers)
    assert result.status_code==200 and result.json()['overall_simple_progress']==100
    pdf=client.post('/api/reports/generate',headers=headers)
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
    assert client.delete(f'/api/xano/tarefas/{tid}',headers=headers).status_code==200
    assert client.delete(f'/api/xano/materias/{sid}',headers=headers).status_code==200


def test_remote_records_cannot_be_read_or_moved_across_users(contract_server):
    a,_=register();b,_=register()
    s=client.post('/api/xano/materias',headers=a,json={'nome':'A'}).json()
    other=client.post('/api/xano/materias',headers=b,json={'nome':'B'}).json()
    t=client.post('/api/xano/tarefas',headers=a,json={'materias_id':s['id'],'titulo_':'T'}).json()
    assert client.get(f"/api/xano/tarefas/{t['id']}",headers=b).status_code==404
    assert client.patch(f"/api/xano/tarefas/{t['id']}",headers=a,json={'materias_id':other['id']}).status_code==404
    assert client.delete(f"/api/xano/materias/{s['id']}",headers=b).status_code==404


def test_contract_integer_hours_reject_fractional_value():
    headers,_=register()
    assert client.post('/api/xano/materias',headers=headers,json={'nome':'A','carga_horaria':2.5}).status_code==422


def test_classroom_is_removed_from_api_and_frontend():
    assert not any('/classroom' in path for path in app.openapi()['paths'])
    assert client.get('/api/classroom/status').status_code==404
    assert 'classroom' not in client.get('/').text.lower()


def test_python_bridge_requires_a_separate_service_key(monkeypatch):
    headers,user=register()
    monkeypatch.setattr(settings,'XANO_PYTHON_BRIDGE_KEY','')
    path=f"/api/integration/search?local_user_id={user['id']}"
    assert client.get(path).status_code==503
    monkeypatch.setattr(settings,'XANO_PYTHON_BRIDGE_KEY','unit-test-bridge')
    assert client.get(path).status_code==401
    result=client.get(path,headers={'X-Integration-Key':'unit-test-bridge'})
    assert result.status_code==200
    pdf=client.post('/api/integration/reports/generate',params={'local_user_id':user['id']},headers={'X-Integration-Key':'unit-test-bridge'})
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')


def test_task_creation_and_metrics_succeed_with_unrelated_unlinked_subject(contract_server):
    tables,_=contract_server
    tables['materias'].append({'id':12,'alunos_id':None,'nome':'Old record','carga_horaria':60})
    headers,user=register()
    subject=client.post('/api/xano/materias',headers=headers,json={'nome':'Owned','carga_horaria':40}).json()
    response=client.post('/api/xano/tarefas',headers=headers,json={
        'materias_id':subject['id'],'titulo_':'Once','status':'pendente',
        'estimated_time_minutes':30,'actual_time_minutes':0})
    assert response.status_code==201,response.text
    assert response.json()['estimated_time_minutes']==30
    assert len(tables['tarefas'])==1
    progress=client.get('/api/analytics/progress',headers=headers)
    assert progress.status_code==200,progress.text
    assert progress.json()['total_subjects']==1 and progress.json()['total_tasks']==1


def test_confirmed_remote_write_followed_by_mirror_failure_is_explicit(contract_server,monkeypatch):
    from fastapi import HTTPException
    from app.services import xano_crud
    tables,_=contract_server
    headers,user=register()
    subject=client.post('/api/xano/materias',headers=headers,json={'nome':'Owned','carga_horaria':40}).json()
    def fail(*args,**kwargs):raise HTTPException(502,'Espelho indisponível.')
    monkeypatch.setattr(xano_crud,'require_mirror',fail)
    response=client.post('/api/xano/tarefas',headers=headers,json={'materias_id':subject['id'],'titulo_':'Once'})
    assert response.status_code==502
    assert len(tables['tarefas'])==1
    assert f"Tarefa {tables['tarefas'][0]['id']} gravada no Xano" in response.json()['detail']
    assert 'Não salve novamente' in response.json()['detail']
