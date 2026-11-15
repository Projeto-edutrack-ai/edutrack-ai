"""Legacy-shaped adapter over the existing local API, for explicit unconfigured/offline mode."""
from app.api import subjects, tasks
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.schemas.task import AcademicTaskCreate, AcademicTaskUpdate
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.services.xano_crud import _prazo, _status_local


def local_student(user):
    return {'id':user.id,'nome':user.name,'email':user.email,'curso':user.course,
            'semestre':1,'source':'local'}


def raw_subject(row):
    return {'id':row.id,'alunos_id':row.user_id,'nome':row.name,'professor':row.professor,
            'descricao':row.description,'carga_horaria':row.workload_hours}


def raw_task(row):
    from datetime import timezone
    due=row.due_date
    if due and due.tzinfo is None:due=due.replace(tzinfo=timezone.utc)
    return {'id':row.id,'materias_id':row.subject_id,'titulo_':row.title,'descricao':row.description,
            'prazo':int(due.timestamp()*1000) if due else None,
            'status':{'pending':'pendente','in_progress':'em_andamento','completed':'concluida'}[row.status],
            'estimated_time_minutes':row.estimated_time_minutes,'actual_time_minutes':row.actual_time_minutes}


class LocalCrudClient:
    def __init__(self,user,db):self.user,self.db=user,db
    def ensure_aluno(self,user):return local_student(user)
    def list_materias(self):
        return [raw_subject(x) for x in self.db.query(Subject).filter(Subject.user_id==self.user.id).all()]
    def list_tarefas(self):
        return [raw_task(x) for x in self.db.query(AcademicTask).filter(AcademicTask.user_id==self.user.id).all()]

    def _request(self,method,path,json_body=None,params=None):
        parts=path.strip('/').split('/');table=parts[0];item_id=int(parts[1]) if len(parts)>1 else None
        data=json_body or {}
        if table=='alunos':
            from app.api.auth import update_user_profile
            from app.schemas.user import UserUpdate
            mapping={'nome':'name','curso':'course','semestre':'college_year'}
            values={mapping[k]:str(v) if k=='semestre' else v for k,v in data.items()}
            update_user_profile(UserUpdate(**values),self.user,self.db)
            return local_student(self.user)
        if table=='materias':
            if method=='DELETE':return subjects.delete_subject(item_id,self.user,self.db)
            mapping={'nome':'name','professor':'professor','descricao':'description','carga_horaria':'workload_hours'}
            values={mapping[k]:v for k,v in data.items() if k in mapping}
            if method=='POST':result=subjects.create_subject(SubjectCreate(**values),self.user,self.db)
            else:result=subjects.update_subject(item_id,SubjectUpdate(**values),self.user,self.db)
            return raw_subject(self.db.get(Subject,result.id))
        if method=='DELETE':return tasks.delete_task(item_id,self.user,self.db)
        mapping={'materias_id':'subject_id','titulo_':'title','descricao':'description',
                 'estimated_time_minutes':'estimated_time_minutes','actual_time_minutes':'actual_time_minutes'}
        values={mapping[k]:v for k,v in data.items() if k in mapping}
        if 'status' in data:values['status']=_status_local(data['status'])
        if 'prazo' in data:values['due_date']=_prazo(data['prazo'])
        if method=='POST':result=tasks.create_task(AcademicTaskCreate(**values),self.user,self.db)
        else:result=tasks.update_task(item_id,AcademicTaskUpdate(**values),self.user,self.db)
        return raw_task(self.db.get(AcademicTask,result.id))
