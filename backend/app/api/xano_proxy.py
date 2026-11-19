"""Authenticated, allowlisted legacy CRUD bridge. Never accepts arbitrary remote URLs."""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session, object_session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.xano_crud import XanoCrudClient, XanoCrudError, _status_local, _prazo, _last_mirror, xano_http_error

router=APIRouter(prefix='/xano',tags=['CRUD Xano autenticado'])


class SubjectPayload(BaseModel):
    model_config=ConfigDict(extra='forbid')
    nome:Optional[str]=Field(None,min_length=1,max_length=500)
    professor:Optional[str]=Field(None,max_length=500)
    descricao:Optional[str]=Field(None,max_length=10000)
    carga_horaria:Optional[int]=Field(None,gt=0)
    @field_validator('nome')
    @classmethod
    def valid_name(cls,value):
        if value is not None and not value.strip():raise ValueError('Nome obrigatório')
        return value.strip() if value else value

    alunos_id:Optional[int]=Field(None,gt=0)  # Checked and overwritten by the server.


class TaskPayload(BaseModel):
    model_config=ConfigDict(extra='forbid')
    materias_id:Optional[int]=Field(None,gt=0)
    titulo_:Optional[str]=Field(None,min_length=1,max_length=500)
    descricao:Optional[str]=Field(None,max_length=10000)
    estimated_time_minutes:Optional[float]=Field(None,ge=0,allow_inf_nan=False)
    actual_time_minutes:Optional[float]=Field(None,ge=0,allow_inf_nan=False)
    prazo:Optional[float]=None  # Xano timestamp in milliseconds, UTC.
    status:Optional[Literal['pendente','em_andamento','em_andamento ','concluida']]=None


def owner_client(user):
    client=XanoCrudClient()
    if not client.is_configured():
        from app.services.local_crud import LocalCrudClient
        return LocalCrudClient(user,object_session(user)),user.id
    try:
        owner=client.ensure_aluno(user)['id']
        client._local_user=user
        return client,owner
    except XanoCrudError as exc:
        raise xano_http_error(exc) from None


def owned_subjects(client,owner):
    return [s for s in client.list_materias() if s.get('alunos_id')==owner]


def owned_tasks(client,owner):
    subject_ids={s['id'] for s in owned_subjects(client,owner)}
    rows=[dict(t) for t in client.list_tarefas() if t.get('materias_id') in subject_ids]
    from app.models.task import AcademicTask
    from sqlalchemy.orm import object_session
    # LocalCrudClient already carries actual time. Remote records receive sidecar metadata.
    if hasattr(client, '_local_user'):
        user=client._local_user
        db=object_session(user)
        metadata={t.xano_id:t for t in db.query(AcademicTask).filter(AcademicTask.user_id==user.id,AcademicTask.xano_id.isnot(None)).all()}
        for row in rows:
            local=metadata.get(row['id'])
            row['actual_time_minutes']=local.actual_time_minutes if local else 0
            row['estimated_time_minutes']=local.estimated_time_minutes if local else 60
    return rows


def owned_record(client,owner,table,item_id):
    rows=owned_subjects(client,owner) if table=='materias' else owned_tasks(client,owner)
    found=next((x for x in rows if x['id']==item_id),None)
    if found is None:raise HTTPException(404,'Registro não encontrado.')
    return found


def invalidate(db,user):
    _last_mirror.pop((str(db.get_bind().url),user.id),None)


def remote_call(client,method,path,payload=None):
    try:return client._request(method,path,json_body=payload)
    except XanoCrudError as exc:raise xano_http_error(exc) from None


@router.get('/alunos/{item_id}')
def get_student(item_id:int,user:User=Depends(get_current_user)):
    client,owner=owner_client(user)
    if item_id!=owner:raise HTTPException(404,'Registro não encontrado.')
    try:return client.ensure_aluno(user)
    except XanoCrudError as exc:raise xano_http_error(exc) from None


class ProfilePayload(BaseModel):
    model_config=ConfigDict(extra='forbid')
    nome:Optional[str]=Field(None,min_length=1,max_length=500)
    curso:Optional[str]=Field(None,max_length=500)
    semestre:Optional[int]=Field(None,ge=1,le=100)


@router.patch('/alunos/{item_id}')
def update_student(item_id:int,payload:ProfilePayload,user:User=Depends(get_current_user)):
    client,owner=owner_client(user)
    if item_id!=owner:raise HTTPException(404,'Registro não encontrado.')
    return remote_call(client,'PATCH',f'/alunos/{item_id}',payload.model_dump(exclude_unset=True))


@router.get('/{table}')
def list_records(table:Literal['materias','tarefas'],user:User=Depends(get_current_user)):
    client,owner=owner_client(user)
    try:return owned_subjects(client,owner) if table=='materias' else owned_tasks(client,owner)
    except XanoCrudError as exc:raise xano_http_error(exc) from None


@router.get('/{table}/{item_id}')
def get_record(table:Literal['materias','tarefas'],item_id:int,user:User=Depends(get_current_user)):
    client,owner=owner_client(user)
    try:return owned_record(client,owner,table,item_id)
    except XanoCrudError as exc:raise xano_http_error(exc) from None


@router.post('/materias',status_code=201)
def create_subject(payload:SubjectPayload,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    client,owner=owner_client(user)
    data=payload.model_dump(exclude_unset=True)
    if not data.get('nome') or not data['nome'].strip():raise HTTPException(422,'Nome obrigatório.')
    if data.get('alunos_id',owner)!=owner:raise HTTPException(403,'Proprietário inválido.')
    data['alunos_id']=owner
    for key in ('professor','descricao'):
        if data.get(key) is None:data[key]=''
    result=remote_call(client,'POST','/materias',data);invalidate(db,user)
    return result


@router.patch('/materias/{item_id}')
def update_subject(item_id:int,payload:SubjectPayload,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    client,owner=owner_client(user)
    try:owned_record(client,owner,'materias',item_id)
    except XanoCrudError as exc:raise xano_http_error(exc) from None
    data=payload.model_dump(exclude_unset=True)
    if data.get('alunos_id',owner)!=owner:raise HTTPException(403,'Proprietário inválido.')
    if any(data.get(k) is None for k in ('nome','carga_horaria') if k in data):raise HTTPException(422,'Campo obrigatório nulo.')
    data['alunos_id']=owner
    for key in ('professor','descricao'):
        if key in data and data[key] is None:data[key]=''
    result=remote_call(client,'PATCH',f'/materias/{item_id}',data);invalidate(db,user)
    return result


def task_data(client,owner,payload,creating=False):
    data=payload.model_dump(exclude_unset=True)
    if creating and (not data.get('titulo_') or not data.get('materias_id')):
        raise HTTPException(422,'Título e disciplina obrigatórios.')
    if any(data.get(k) is None for k in ('titulo_','materias_id','status') if k in data):
        raise HTTPException(422,'Campo obrigatório nulo.')
    if 'titulo_' in data and not data['titulo_'].strip():raise HTTPException(422,'Título obrigatório.')
    if 'materias_id' in data:owned_record(client,owner,'materias',data['materias_id'])
    if creating:data.setdefault('status','pendente')
    if 'status' in data:
        _status_local(data['status'])
        if data['status']=='em_andamento':data['status']='em_andamento '
    if 'prazo' in data:_prazo(data['prazo'])
    if 'descricao' in data and data['descricao'] is None:data['descricao']=''
    return data


@router.post('/tarefas',status_code=201)
def create_task(payload:TaskPayload,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    client,owner=owner_client(user)
    try:data=task_data(client,owner,payload,creating=True)
    except XanoCrudError as exc:raise xano_http_error(exc) from None
    result=write_task(client,owner,'POST','/tarefas',data,db,user)
    return result


@router.patch('/tarefas/{item_id}')
def update_task(item_id:int,payload:TaskPayload,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    client,owner=owner_client(user)
    try:
        owned_record(client,owner,'tarefas',item_id)
        data=task_data(client,owner,payload)
    except XanoCrudError as exc:raise xano_http_error(exc) from None
    return write_task(client,owner,'PATCH',f'/tarefas/{item_id}',data,db,user)


@router.delete('/{table}/{item_id}')
def delete_record(table:Literal['materias','tarefas'],item_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    client,owner=owner_client(user)
    try:owned_record(client,owner,table,item_id)
    except XanoCrudError as exc:raise xano_http_error(exc) from None
    remote_call(client,'DELETE',f'/{table}/{item_id}');invalidate(db,user)
    return {'id':item_id,'message':'Registro excluído.'}


def write_task(client,owner,method,path,data,db,user):
    from app.services.local_crud import LocalCrudClient
    from app.services.xano_crud import require_mirror
    from app.models.task import AcademicTask
    metadata={k:data.pop(k) for k in ('estimated_time_minutes','actual_time_minutes') if k in data}
    if any(v is None for v in metadata.values()):raise HTTPException(422,'Tempo não pode ser nulo.')
    if isinstance(client,LocalCrudClient):
        return remote_call(client,method,path,{**data,**metadata})
    result=remote_call(client,method,path,data)
    invalidate(db,user)
    try:
        require_mirror(db,user,force=True)
    except HTTPException as exc:
        remote_id=result.get('id') if isinstance(result,dict) else None
        if type(remote_id) is int and remote_id>0:
            raise HTTPException(exc.status_code,f'Tarefa {remote_id} gravada no Xano, mas a atualização local falhou. Não salve novamente; confira a lista antes de repetir. '+str(exc.detail),headers=exc.headers) from None
        raise
    if not isinstance(result,dict) or not isinstance(result.get('id'),int):
        raise HTTPException(502,'Operação remota não retornou o identificador da tarefa.')
    row=db.query(AcademicTask).filter(AcademicTask.user_id==user.id,AcademicTask.xano_id==result['id']).first()
    if row is None:raise HTTPException(502,'Tarefa gravada mas ainda não disponível no espelho; recarregue antes de tentar novamente.')
    for k,v in metadata.items():setattr(row,k,v)
    db.commit()
    return {**result,'estimated_time_minutes':row.estimated_time_minutes,'actual_time_minutes':row.actual_time_minutes}
