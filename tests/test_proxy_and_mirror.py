import json
from datetime import datetime
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.services.xano_crud import XanoCrudClient,XanoCrudError,mirror_user_data,_prazo
from test_xano_sync_and_reset import fake_xano
from test_adequacao import register

client=TestClient(app)


def test_local_proxy_full_flow_and_metadata():
    headers,user=register()
    result=client.post('/api/xano/materias',headers=headers,json={'nome':'Teste local','carga_horaria':80})
    assert result.status_code==201,result.text
    sid=result.json()['id']
    result=client.post('/api/xano/tarefas',headers=headers,json={'materias_id':sid,'titulo_':'Lista','status':'pendente','estimated_time_minutes':95})
    assert result.status_code==201,result.text
    tid=result.json()['id']
    assert result.json()['estimated_time_minutes']==95
    result=client.post(f'/api/academic_tasks/by-xano/{tid}/study-time',headers=headers,json={'additional_minutes':12,'new_status':'completed'})
    assert result.status_code==200,result.text
    assert result.json()['actual_time_minutes']==12
    assert client.get('/api/analytics/progress',headers=headers).json()['overall_simple_progress']==100
    result=client.get(f'/api/xano/tarefas/{tid}',headers=headers)
    assert result.json()['status']=='concluida' and result.json()['actual_time_minutes']==12


def test_local_proxy_blocks_foreign_records_and_forged_owner():
    a,ua=register();b,ub=register()
    s=client.post('/api/xano/materias',headers=a,json={'nome':'A'}).json()
    foreign=client.post('/api/xano/materias',headers=b,json={'nome':'B'}).json()
    t=client.post('/api/xano/tarefas',headers=a,json={'materias_id':s['id'],'titulo_':'Tarefa'}).json()
    assert client.get(f"/api/xano/materias/{s['id']}",headers=b).status_code==404
    assert client.delete(f"/api/xano/tarefas/{t['id']}",headers=b).status_code==404
    assert client.patch(f"/api/xano/tarefas/{t['id']}",headers=a,json={'materias_id':foreign['id']}).status_code==404
    assert client.post('/api/xano/materias',headers=a,json={'nome':'Inválida','alunos_id':ub['id']}).status_code==403
    assert client.get('/api/xano/materias').status_code==401
    assert client.post('/api/xano/tarefas',headers=a,json={'materias_id':s['id'],'titulo_':'T','user_id':ub['id']}).status_code==422


def test_existing_remote_email_does_not_grant_ownership(fake_xano):
    fake_xano.tables['alunos'].append({'id':900000,'nome':'Remoto','email':'preexisting@example.com'})
    result=client.post('/api/auth/register',json={'name':'Outro','email':'preexisting@example.com','password':'senha123'})
    assert result.status_code==201
    assert result.json()['xano_sync']['status']=='link_required'
    headers={'Authorization':'Bearer '+result.json()['access_token']}
    assert client.get('/api/xano/materias',headers=headers).status_code==502


@pytest.mark.parametrize('responses',[
    [{'unexpected':[]}],
    [{'items':[]}],
    [{'items':[{'id':1}],'nextPage':1}],
    [[{'id':1},{'id':1}]],
    [[{'id':1},None]],
])
def test_invalid_or_incomplete_pagination_is_not_an_empty_snapshot(responses):
    def answer(request):return httpx.Response(200,json=responses.pop(0) if len(responses)>1 else responses[0])
    api=XanoCrudClient(base_url='https://example.test',transport=httpx.MockTransport(answer))
    with pytest.raises(XanoCrudError):api.list_materias()


def test_pagination_requires_complete_dataset_and_service_header(monkeypatch):
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_HEADER','X-Service-Key')
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_VALUE','unit-test-only')
    def answer(request):
        assert request.headers['X-Service-Key']=='unit-test-only'
        if request.url.params.get('page')=='2':return httpx.Response(200,json={'items':[{'id':2}],'nextPage':None})
        return httpx.Response(200,json={'items':[{'id':1}],'nextPage':2})
    api=XanoCrudClient(base_url='https://example.test',transport=httpx.MockTransport(answer))
    assert [r['id'] for r in api.list_materias()]==[1,2]


def test_mirror_rolls_back_changes_on_invalid_row(fake_xano):
    headers,user=register()
    db=SessionLocal()
    try:
        u=db.get(User,user['id']);owner=u.xano_aluno_id
        fake_xano.tables['materias']=[{'id':801,'alunos_id':owner,'nome':'Original','carga_horaria':60}]
        assert mirror_user_data(db,u,force=True)['status']=='synced'
        fake_xano.tables['materias']=[{'id':801,'alunos_id':owner,'nome':'Não persistir','carga_horaria':80},
                                     {'id':802,'alunos_id':owner,'nome':'Inválida','carga_horaria':'erro'}]
        assert mirror_user_data(db,u,force=True)['status']=='failed'
        db.expire_all()
        assert db.query(Subject).filter_by(user_id=u.id,xano_id=801).one().name=='Original'
        assert db.query(Subject).filter_by(user_id=u.id,xano_id=802).count()==0
    finally:db.close()


def test_mirror_keeps_data_on_malformed_remote_snapshot(fake_xano,monkeypatch):
    headers,user=register()
    db=SessionLocal()
    try:
        u=db.get(User,user['id']);owner=u.xano_aluno_id
        fake_xano.tables['materias']=[{'id':901,'alunos_id':owner,'nome':'Preservar','carga_horaria':60}]
        assert mirror_user_data(db,u,force=True)['status']=='synced'
        fake_xano.tables['materias']=[{'id':901}]  # Missing owner is malformed, not a deletion.
        assert mirror_user_data(db,u,force=True)['status']=='failed'
        assert db.query(Subject).filter_by(user_id=u.id,xano_id=901).count()==1
    finally:db.close()


def test_deadline_offset_is_converted_to_utc():
    assert _prazo('2026-11-10T12:00:00-03:00')==datetime(2026,11,10,15)


def test_xano_metrics_exclude_local_demo_rows(fake_xano):
    headers,user=register()
    with SessionLocal() as db:
        u=db.get(User,user['id'])
        db.add(Subject(user_id=u.id,name='Não misturar',source='local',workload_hours=60));db.commit()
        fake_xano.tables['materias']=[{'id':1001,'alunos_id':u.xano_aluno_id,'nome':'Remota','carga_horaria':60}]
    result=client.get('/api/analytics/progress',headers=headers)
    assert result.status_code==200,result.text
    assert result.json()['total_subjects']==1
    assert result.json()['subjects_breakdown'][0]['subject_name']=='Remota'


def test_legacy_unlinked_rows_do_not_block_other_users_mirror(fake_xano):
    _,user=register()
    with SessionLocal() as db:
        u=db.get(User,user['id']);owner=u.xano_aluno_id
        fake_xano.tables['materias']=[{'id':12,'alunos_id':None,'nome':'Legada sem dono'},
            {'id':1401,'alunos_id':owner,'nome':'Minha matéria','carga_horaria':40},
            {'id':1402,'alunos_id':owner+10000,'nome':'Outra conta','carga_horaria':'irrelevante'}]
        fake_xano.tables['tarefas']=[{'id':1501,'materias_id':1401,'titulo_':'Minha tarefa','status':'pendente'},
            {'id':1502,'materias_id':None,'titulo_':'Sem vínculo','status':'invalid'},
            {'id':1503,'materias_id':12,'titulo_':'Legada','status':'invalid'}]
        assert mirror_user_data(db,u,force=True)['status']=='synced'
        assert [s.xano_id for s in db.query(Subject).filter_by(user_id=u.id,source='xano')]==[1401]
        assert [t.xano_id for t in db.query(AcademicTask).filter_by(user_id=u.id,source='xano')]==[1501]
        assert fake_xano.tables['materias'][0]['alunos_id'] is None


def test_known_task_losing_parent_does_not_disappear(fake_xano):
    _,user=register()
    with SessionLocal() as db:
        u=db.get(User,user['id'])
        fake_xano.tables['materias']=[{'id':1601,'alunos_id':u.xano_aluno_id,'nome':'Minha','carga_horaria':40}]
        fake_xano.tables['tarefas']=[{'id':1602,'materias_id':1601,'titulo_':'Preservar','status':'pendente'}]
        assert mirror_user_data(db,u,force=True)['status']=='synced'
        fake_xano.tables['tarefas'][0]['materias_id']=None
        assert mirror_user_data(db,u,force=True)['status']=='failed'
        assert db.query(AcademicTask).filter_by(user_id=u.id,xano_id=1602).count()==1
