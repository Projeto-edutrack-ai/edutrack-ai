"""Run from the project root. GETs and a read-only SQLite inspection only."""
import json
import math
import sys
from pathlib import Path


def positive(value):
    return type(value) is int and value>0


def summarize(subjects,tasks):
    result={
        'quantidade_materias':len(subjects),'quantidade_tarefas':len(tasks),
        'materias_com_aluno_invalido':[], 'tarefas_com_materia_invalida':[],
        'tarefas_com_status_invalido':[], 'materias_com_carga_invalida':[],
        'tarefas_com_prazo_invalido':[],
    }
    for row in subjects:
        rid=row.get('id')
        if not positive(row.get('alunos_id')):result['materias_com_aluno_invalido'].append(rid)
        try:
            hours=float(row.get('carga_horaria') or 60)
            if not math.isfinite(hours) or hours<=0:raise ValueError()
        except (ValueError,TypeError):result['materias_com_carga_invalida'].append(rid)
    for row in tasks:
        rid=row.get('id')
        if not positive(row.get('materias_id')):result['tarefas_com_materia_invalida'].append(rid)
        if str(row.get('status',row.get('status_')) or '').strip().lower() not in {'pendente','em_andamento','concluida','pending','in_progress','completed'}:
            result['tarefas_com_status_invalido'].append(rid)
        value=row.get('prazo')
        if value is not None and value!='':
            from datetime import datetime,timezone
            try:
                if isinstance(value,(int,float)) and not isinstance(value,bool):datetime.fromtimestamp(value/1000,tz=timezone.utc)
                elif isinstance(value,str):datetime.fromisoformat(value.replace('Z','+00:00'))
                else:raise ValueError()
            except (ValueError,OverflowError,OSError):result['tarefas_com_prazo_invalido'].append(rid)
    return result


def main():
    root=Path.cwd()
    if not (root/'backend/app').is_dir():
        print('Abra o terminal na pasta que contém run_server.py antes de executar.');return 1
    sys.path.insert(0,str(root/'backend'))
    from dotenv import load_dotenv
    load_dotenv(root/'.env')
    from app.services.xano_crud import XanoCrudClient,XanoCrudError
    c=XanoCrudClient()
    try:
        subjects=c.list_materias()
        tasks=c.list_tarefas()
    except XanoCrudError as exc:
        from app.services.xano_request_budget import XanoRateLimited
        if isinstance(exc,XanoRateLimited):print('Xano temporariamente limitado. Aguarde antes de repetir o diagnóstico.')
        else:print('Falha na leitura Xano. Confira serviço/URL/chave; nenhuma chave foi exibida.')
        return 1
    report=summarize(subjects,tasks)
    # Inspect schema without opening the application's writable Session.
    try:
        import sqlite3
        from sqlalchemy.engine import make_url
        from app.core.config import settings
        from app.models.subject import Subject
        from app.models.task import AcademicTask
        from app.models.user import User
        url=make_url(settings.DATABASE_URL)
        if url.drivername.startswith('sqlite') and url.database and url.database!=':memory:':
            dbpath=Path(url.database).resolve()
            with sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True) as db:
                db.execute('PRAGMA query_only=ON')
                missing={}
                for model in [User,Subject,AcademicTask]:
                    table=model.__tablename__
                    present={row[1] for row in db.execute(f'PRAGMA table_info({table})')}
                    absent=sorted({column.name for column in model.__table__.columns}-present)
                    if absent:missing[table]=absent
                report['colunas_locais_ausentes']=missing
        else:report['schema_local']='tipo_de_banco_nao_inspecionado'
    except Exception:
        report['schema_local']='inspecao_indisponivel_sem_alteracoes'
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print('Somente consultas. Nenhum registro ou credencial foi alterado ou exibido.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
