"""Deterministic budget tests: no waiting and no external network."""
from concurrent.futures import ThreadPoolExecutor
import threading
import pytest
from app.services.xano_request_budget import RequestBudget, XanoRateLimited, budget_for
from app.services.xano_crud import XanoCrudClient, xano_http_error
import httpx

class Clock:
    def __init__(self):self.now=100.0;self.sleeps=[]
    def __call__(self):return self.now
    def sleep(self,seconds):self.sleeps.append(seconds);self.now+=seconds


def test_concurrent_reads_singleflight_and_return_independent_copies():
    b=RequestBudget(interval=0);count=[];barrier=threading.Barrier(6)
    def read():
        barrier.wait()
        return b.run(('credential-a','/materias'),'GET',lambda:count.append(1) or [{'id':1}])
    with ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(lambda _:read(),range(6)))
    assert len(count)==1
    rows[0][0]['id']=99
    assert rows[1][0]['id']==1


def test_expiration_credential_isolation_and_spacing():
    clock=Clock();b=RequestBudget(clock=clock,sleep=clock.sleep)
    calls=[]
    op=lambda:calls.append(clock()) or [len(calls)]
    assert b.run(('secret-a','/materias'),'GET',op)==[1]
    assert b.run(('secret-a','/materias'),'GET',op)==[1]
    assert b.run(('secret-b','/materias'),'GET',op)==[2]
    assert clock.sleeps==[pytest.approx(2.1)]
    clock.now+=31
    assert b.run(('secret-a','/materias'),'GET',op)==[3]


def test_write_invalidates_reads_and_never_retries_after_uncertain_failure():
    b=RequestBudget(interval=0);calls=[]
    b.run('list','GET',lambda:[1])
    def fail():calls.append('write');raise RuntimeError('connection lost')
    with pytest.raises(RuntimeError):b.run('create','POST',fail)
    assert calls==['write']
    assert b.run('list','GET',lambda:[1,2])==[1,2]


def test_429_pauses_remote_requests_without_sleeping_or_replaying_writes():
    clock=Clock();b=RequestBudget(clock=clock,sleep=clock.sleep);calls=[]
    def limited():calls.append(1);raise XanoRateLimited(45)
    with pytest.raises(XanoRateLimited):b.run('write','POST',limited)
    with pytest.raises(XanoRateLimited):b.run('read','GET',lambda:calls.append(2))
    assert calls==[1] and clock.sleeps==[]
    clock.now+=46
    assert b.run('read','GET',lambda:[3])==[3]


def test_budget_is_shared_by_instance_not_path():
    assert budget_for('https://shared-budget.test/api:a') is budget_for('https://shared-budget.test/api:b')
    assert budget_for('https://shared-budget.test/api:a') is not budget_for('https://other-budget.test/api:a')


def test_client_429_is_typed_and_exposed_as_429_not_expired_session():
    c=XanoCrudClient(base_url='https://mock.test',transport=httpx.MockTransport(lambda _:httpx.Response(429,headers={'Retry-After':'40'})))
    with pytest.raises(XanoRateLimited) as exc:c._request('GET','/materias')
    error=xano_http_error(exc.value)
    assert error.status_code==429
    assert error.headers['Retry-After']=='40'


def test_real_client_path_shares_cache_invalidates_and_separates_credentials(monkeypatch):
    from app.services import xano_request_budget as module
    from app.core.config import settings
    base='https://client-budget.test/api:one'
    monkeypatch.setitem(module._budgets,'client-budget.test',RequestBudget(interval=0))
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_VALUE','private-a')
    calls=[]
    def send(self,method,path,json_body=None,params=None):
        calls.append((method,path));return [{'id':len(calls)}]
    monkeypatch.setattr(XanoCrudClient,'_send_request',send)
    a=XanoCrudClient(base_url=base);b=XanoCrudClient(base_url=base)
    assert a._request('GET','/materias')==b._request('GET','/materias')
    assert len(calls)==1
    monkeypatch.setattr(settings,'XANO_CRUD_AUTH_VALUE','private-b')
    b._request('GET','/materias');assert len(calls)==2
    b._request('POST','/materias',json_body={'nome':'Test'})
    b._request('GET','/materias');assert len(calls)==4
