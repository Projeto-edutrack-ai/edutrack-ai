"""Regression coverage: source consistency, ownership, search, PDF and gateway failure."""
from datetime import datetime, timedelta, timezone
import json
import subprocess
import sys
from pathlib import Path
import uuid
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

from app.services.progress_calculation import calculate_percentage

client = TestClient(app)


def register():
    result = client.post('/api/auth/register', json={
        'name': 'Teste adequação', 'email': f'{uuid.uuid4().hex}@example.com', 'password': 'Teste123456!'})
    assert result.status_code == 201, result.text
    data = result.json()
    return {'Authorization': 'Bearer '+data['access_token']}, data['user']


def subject(headers, name='Matéria de teste'):
    r = client.post('/api/subjects', headers=headers, json={'name': name, 'workload_hours':60})
    assert r.status_code == 201, r.text
    return r.json()


def task(headers, subject_id, **overrides):
    data = dict(subject_id=subject_id, title='Tarefa', status='pending')
    data.update(overrides)
    r = client.post('/api/academic_tasks', headers=headers, json=data)
    assert r.status_code == 201, r.text
    return r.json()


def test_crud_progress_report_and_cross_user_access():
    a, _ = register(); b, _ = register()
    s = subject(a, 'Disciplina de integração'); foreign = subject(b)
    t = task(a,s['id'])
    assert client.patch(f"/api/subjects/{s['id']}", headers=a, json={'professor':'Professora'}).status_code == 200
    assert client.patch(f"/api/academic_tasks/{t['id']}", headers=a,json={'status':'completed'}).status_code == 200
    assert client.get('/api/analytics/progress',headers=a).json()['overall_simple_progress'] == 100
    assert len(client.get('/api/subjects',headers=b).json()) == 1
    for method in ('get','patch','delete'):
        options = {'json': {'name':'Invadida'}} if method == 'patch' else {}
        assert getattr(client,method)(f"/api/subjects/{s['id']}",headers=b,**options).status_code == 404
        options = {'json': {'title':'Invadida'}} if method == 'patch' else {}
        assert getattr(client,method)(f"/api/academic_tasks/{t['id']}",headers=b,**options).status_code == 404
    assert client.patch(f"/api/academic_tasks/{t['id']}",headers=a,json={'subject_id':foreign['id']}).status_code == 404
    for payload in ({'status':'inventado'}, {'status':None}, {'actual_time_minutes':-1}):
        assert client.patch(f"/api/academic_tasks/{t['id']}",headers=a,json=payload).status_code == 422
    assert client.patch(f"/api/subjects/{s['id']}",headers=a,json={'workload_hours':None}).status_code == 422
    report = client.post('/api/reports/generate',headers=a)
    assert report.status_code == 200 and report.content.startswith(b'%PDF')
    assert 'attachment' in report.headers['content-disposition']
    assert client.post('/api/reports/generate').status_code == 401


def test_search_name_or_overdue_and_owner():
    a,_ = register(); b,_ = register()
    named=subject(a,'Álgebra'); late=subject(a,'Física'); done=subject(a,'História'); other=subject(b,'Outra')
    past=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat()
    task(a,late['id'],due_date=past)
    task(a,done['id'],due_date=past,status='completed')
    task(a,done['id'],due_date=(datetime.now(timezone.utc)+timedelta(days=2)).isoformat())
    task(a,done['id']); task(b,other['id'],due_date=past)
    data=client.get('/api/search',headers=a,params={'q':'Álgebra','overdue':'true'}).json()
    assert {s['id'] for s in data['subjects']} == {named['id'],late['id']}
    data=client.get('/api/search',headers=a,params={'overdue':'true'}).json()
    assert {s['id'] for s in data['subjects']} == {late['id']} and len(data['tasks']) == 1
    assert client.get('/api/search',headers=a,params={'q':'%'}).json()['total_matches'] == 0
    assert client.get('/api/search',headers=a).json()['total_matches'] == 0


@pytest.mark.parametrize('tasks, expected', [([],0),([{'status':'completed'},{'status':'pending'}],50),([{'status':'completed'}],100)])
def test_progress_cli_and_service(tasks,expected):
    assert calculate_percentage(tasks)==expected
    script=Path(__file__).resolve().parents[1]/'scripts/calculate_progress.py'
    result=subprocess.run([sys.executable,str(script),'--tasks',json.dumps(tasks)],capture_output=True,text=True)
    assert result.returncode==0, result.stderr
    assert json.loads(result.stdout)=={'percentage':expected}


def test_progress_cli_rejects_bad_status():
    script=Path(__file__).resolve().parents[1]/'scripts/calculate_progress.py'
    result=subprocess.run([sys.executable,str(script),'--tasks','[{"status":"done"}]'],capture_output=True,text=True)
    assert result.returncode==2 and not result.stdout
