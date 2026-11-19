"""Server-only legacy Xano adapter and validated, transactional SQLite mirror.

Field and authentication configuration must be verified against the real API docs.
No remote network access occurs merely by importing this module.
"""
import logging
import time
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session, object_session
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User

log = logging.getLogger("edutrack.xano")
_MAX_PAGES = 50
_last_mirror = {}
_locks = {}
_locks_guard = threading.Lock()
MIRROR_MIN_INTERVAL_SECONDS = 3.0


from app.services.xano_request_budget import XanoCrudError, XanoRateLimited, budget_for


def xano_http_error(exc):
    if isinstance(exc,XanoRateLimited):
        return HTTPException(429,str(exc),headers={"Retry-After":str(exc.retry_after)})
    return HTTPException(502,str(exc))


class XanoLinkRequired(XanoCrudError):
    pass


def positive_id(value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise XanoCrudError("Identificador inválido na resposta Xano")
    return value


class XanoCrudClient:
    def __init__(self, base_url=None, timeout=None, transport=None):
        self._base = ((settings.XANO_CRUD_BASE_URL if base_url is None else base_url) or "").strip().rstrip("/")
        self._timeout = settings.XANO_TIMEOUT_SECONDS if timeout is None else timeout
        self._transport = transport

    def is_configured(self):
        return self._base.lower().startswith(("https://", "http://"))

    def _request(self, method, path, json_body=None, params=None):
        # Unit-test transports remain isolated; the budget itself is tested independently.
        if self._transport is not None:
            return self._send_request(method,path,json_body,params)
        if not settings.XANO_CRUD_AUTH_VALUE:
            raise XanoCrudError("Configure a credencial de serviço no backend")
        import hashlib
        import json
        fingerprint=hashlib.sha256(settings.XANO_CRUD_AUTH_VALUE.encode()).hexdigest()
        key=(self._base,settings.XANO_CRUD_AUTH_HEADER,fingerprint,path,json.dumps(params,sort_keys=True))
        return budget_for(self._base).run(key,method,lambda:self._send_request(method,path,json_body,params))

    def _send_request(self, method, path, json_body=None, params=None):
        if not self.is_configured():
            raise XanoCrudError("XANO_CRUD_BASE_URL não configurada")
        if not self._base.startswith("https://") and self._transport is None:
            raise XanoCrudError("A API remota precisa usar HTTPS")
        headers = {"Accept": "application/json"}
        if settings.XANO_CRUD_AUTH_VALUE:
            headers[settings.XANO_CRUD_AUTH_HEADER] = settings.XANO_CRUD_AUTH_VALUE
        elif self._transport is None:
            raise XanoCrudError("Configure a credencial de serviço XANO_CRUD_AUTH_VALUE no backend e proteja as rotas no Xano")
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport, follow_redirects=False) as http:
                response = http.request(method, self._base + path, json=json_body, params=params, headers=headers)
        except httpx.HTTPError as exc:
            raise XanoCrudError("Falha de comunicação com Xano") from exc
        if response.status_code == 429:
            raise XanoRateLimited(response.headers.get("Retry-After",20))
        if response.status_code >= 300:
            raise XanoCrudError(f"Xano respondeu HTTP {response.status_code}")
        if response.status_code == 204:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise XanoCrudError("Resposta Xano não é JSON válido") from exc

    def list_all(self, path):
        items, page, visited, seen_ids = [], 1, set(), set()
        while len(visited) < _MAX_PAGES:
            if page in visited:
                raise XanoCrudError("Ciclo de paginação Xano")
            visited.add(page)
            data = self._request("GET", path, params={"page":page} if page != 1 else None)
            if isinstance(data, list):
                rows, next_page = data, None
            elif isinstance(data, dict) and isinstance(data.get("items"), list) and "nextPage" in data:
                rows, next_page = data["items"], data["nextPage"]
            else:
                raise XanoCrudError("Lista Xano inválida ou sem metadados de paginação")
            for row in rows:
                if not isinstance(row, dict):
                    raise XanoCrudError("Registro Xano inválido")
                row_id = positive_id(row.get("id"))
                if row_id in seen_ids:
                    raise XanoCrudError("Registro duplicado na paginação Xano")
                seen_ids.add(row_id)
                items.append(row)
            if next_page is None or next_page is False or next_page == 0:
                return items
            page = positive_id(next_page)
        raise XanoCrudError("Listagem Xano incompleta: limite de páginas atingido")

    def find_aluno_by_email(self, email):
        matches = [a for a in self.list_all('/alunos') if str(a.get('email') or '').strip().lower() == email.strip().lower()]
        if len(matches) > 1:
            raise XanoLinkRequired("E-mail duplicado no Xano; revise o vínculo administrativamente")
        return matches[0] if matches else None

    def ensure_aluno(self, user):
        bound = getattr(user, 'xano_aluno_id', None)
        if bound is not None:
            if getattr(user, 'xano_binding_base', None) != self._base:
                raise XanoLinkRequired('A API configurada difere da API do vínculo; revisão administrativa necessária')
            rows = [a for a in self.list_all('/alunos') if a['id'] == bound]
            if not rows:
                raise XanoLinkRequired("Aluno vinculado não encontrado; revise o vínculo")
            return rows[0]
        if self.find_aluno_by_email(user.email):
            raise XanoLinkRequired("Aluno remoto já existe. Vinculação administrativa verificada necessária; e-mail não comprova propriedade")
        created = self._request('POST', '/alunos', json_body={
            'nome':user.name, 'email':user.email, 'curso':user.course or 'Ciência da Computação',
            'semestre':_semestre(user.college_year)})
        if not isinstance(created,dict):
            raise XanoCrudError('O Xano não devolveu o aluno criado')
        user.xano_aluno_id = positive_id(created.get('id'))
        user.xano_binding_base = self._base
        db = object_session(user)
        if db:
            db.commit()
        return created

    def list_materias(self):
        return self.list_all('/materias')

    def list_tarefas(self):
        return self.list_all('/tarefas')


def _semestre(value):
    import re
    match = re.search(r'\d+', value or '')
    return max(1,int(match.group())) if match else 1


def sync_aluno(user, client=None):
    client = client or XanoCrudClient()
    if not client.is_configured():
        from app.services.local_crud import local_student
        return {'status':'skipped','detail':'Modo local; Xano não configurado','aluno':local_student(user) if object_session(user) else None}
    try:
        aluno = client.ensure_aluno(user)
        return {'status':'synced','detail':'Aluno vinculado ao Xano','aluno':aluno}
    except XanoLinkRequired as exc:
        return {'status':'link_required','detail':str(exc),'aluno':None}
    except XanoCrudError as exc:
        return {'status':'failed','detail':str(exc),'aluno':None}


def _status_local(raw):
    value = str(raw or '').strip().lower()
    values = {'pendente':'pending','pending':'pending','em_andamento':'in_progress',
              'in_progress':'in_progress','concluida':'completed','completed':'completed'}
    if value not in values:
        raise XanoCrudError('Status remoto desconhecido')
    return values[value]


def _prazo(value):
    if value is None or value == '':
        return None
    try:
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            result = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        elif isinstance(value,str):
            result = datetime.fromisoformat(value.replace('Z','+00:00'))
        else:
            raise ValueError()
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError,OverflowError,OSError):
        raise XanoCrudError('Prazo remoto inválido') from None



def linked_rows(rows, field, known_ids):
    """Ignore unowned legacy rows, but never confuse a broken known link with deletion."""
    valid=[]
    for row in rows:
        try:
            positive_id(row.get(field))
        except XanoCrudError:
            if row['id'] in known_ids:
                raise XanoCrudError('Um registro já vinculado à sua conta perdeu a referência no Xano; dados locais preservados.') from None
            continue
        valid.append(row)
    return valid


def mirror_user_data(db, user, client=None, force=False):
    client = client or XanoCrudClient()
    if not client.is_configured():
        return {'status':'skipped','detail':'Xano não configurado'}
    key = (str(db.get_bind().url), user.id)
    with _locks_guard:
        lock = _locks.setdefault(key,threading.Lock())
    with lock:
        if not force and time.monotonic() - _last_mirror.get(key,0) < MIRROR_MIN_INTERVAL_SECONDS:
            return {'status':'cached','detail':'Espelho recente'}
        try:
            aluno = client.ensure_aluno(user)
            owner = positive_id(aluno.get('id'))
            all_subjects = client.list_materias()
            # Only the current user's known records can make a broken link ambiguous.
            known_subjects={s.xano_id for s in db.query(Subject).filter(Subject.user_id==user.id,Subject.xano_id.isnot(None)).all()}
            valid_subjects=linked_rows(all_subjects,'alunos_id',known_subjects)
            subjects = [m for m in valid_subjects if m['alunos_id'] == owner]
            subject_ids = {m['id'] for m in subjects}
            all_tasks = client.list_tarefas()
            known_tasks={t.xano_id for t in db.query(AcademicTask).filter(AcademicTask.user_id==user.id,AcademicTask.xano_id.isnot(None)).all()}
            valid_tasks=linked_rows(all_tasks,'materias_id',known_tasks)
            tasks = [t for t in valid_tasks if t['materias_id'] in subject_ids]
            validated = []
            for t in tasks:
                validated.append((t, _status_local(t.get('status',t.get('status_'))), _prazo(t.get('prazo'))))
            # Mutations start only after the complete remote snapshot has been validated.
            with db.begin_nested():
                local_subjects = {s.xano_id:s for s in db.query(Subject).filter(Subject.user_id==user.id,Subject.xano_id.isnot(None)).all()}
                for m in subjects:
                    s = local_subjects.get(m['id'])
                    if s is None:
                        s=Subject(user_id=user.id,xano_id=m['id'],source='xano',name=m.get('nome') or 'Sem nome')
                        db.add(s);local_subjects[m['id']]=s
                    s.name=m.get('nome') or s.name
                    s.professor=m.get('professor') or None
                    s.description=m.get('descricao') or None
                    try:
                        hours=float(m.get('carga_horaria') or 60)
                    except (ValueError,TypeError):
                        raise XanoCrudError('Carga horária remota inválida')
                    import math
                    if not math.isfinite(hours) or hours<=0:
                        raise XanoCrudError('Carga horária remota inválida')
                    s.workload_hours=hours
                db.flush()
                local_tasks={t.xano_id:t for t in db.query(AcademicTask).filter(AcademicTask.user_id==user.id,AcademicTask.xano_id.isnot(None)).all()}
                now=datetime.now(timezone.utc).replace(tzinfo=None)
                for remote,status,due in validated:
                    t=local_tasks.get(remote['id'])
                    if t is None:
                        t=AcademicTask(user_id=user.id,xano_id=remote['id'],source='xano',title='',subject_id=local_subjects[remote['materias_id']].id)
                        db.add(t);local_tasks[remote['id']]=t
                    t.subject_id=local_subjects[remote['materias_id']].id
                    t.title=remote.get('titulo_') or remote.get('titulo') or 'Sem título'
                    t.description=remote.get('descricao') or None
                    t.due_date=due;t.status=status
                    if status=='completed' and t.completed_at is None:t.completed_at=now
                    if status!='completed':t.completed_at=None
                keep={t['id'] for t in tasks}
                for xid,t in local_tasks.items():
                    if xid not in keep:db.delete(t)
                for xid,s in local_subjects.items():
                    if xid not in subject_ids:db.delete(s)
                db.flush()
            db.commit()
        except XanoRateLimited as exc:
            db.rollback()
            return {'status':'failed','detail':str(exc),'http_status':429,'retry_after':exc.retry_after}
        except (XanoCrudError,KeyError,TypeError,ValueError) as exc:
            db.rollback()
            return {'status':'failed','detail':str(exc)}
        except SQLAlchemyError:
            db.rollback()
            return {'status':'failed','detail':'Falha ao atualizar o espelho local; dados preservados'}
        _last_mirror[key]=time.monotonic()
        return {'status':'synced','detail':'Espelho atualizado','subjects':len(subjects),'tasks':len(tasks)}


def require_mirror(db,user,force=False):
    result=mirror_user_data(db,user,force=force)
    if result['status']=='failed':
        if result.get('http_status')==429:
            raise HTTPException(429,result['detail'],headers={'Retry-After':str(result['retry_after'])})
        raise HTTPException(status_code=502,detail='Não foi possível atualizar os dados Xano. Tente novamente ou revise o vínculo/configuração.')
    return result


from contextlib import contextmanager
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria

@contextmanager
def academic_source_scope(db):
    """Read-only services exclude local/demo rows when the Xano source is configured."""
    if not XanoCrudClient().is_configured():
        yield
        return
    def restrict(state):
        if state.is_select:
            state.statement=state.statement.options(
                with_loader_criteria(Subject, Subject.xano_id.isnot(None), include_aliases=True),
                with_loader_criteria(AcademicTask, AcademicTask.xano_id.isnot(None), include_aliases=True))
    event.listen(db, 'do_orm_execute', restrict)
    try:
        yield
    finally:
        event.remove(db, 'do_orm_execute', restrict)
