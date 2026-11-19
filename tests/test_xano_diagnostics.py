import importlib.util
import json
from pathlib import Path


def test_report_identifies_bad_references_without_echoing_private_fields():
    path=Path(__file__).resolve().parents[1]/'scripts/diagnostico_edutrack.py'
    spec=importlib.util.spec_from_file_location('xano_diag',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.summarize(
        [{'id':9,'alunos_id':None,'nome':'PRIVATE_NAME','email':'PRIVATE_EMAIL','carga_horaria':40}],
        [{'id':11,'materias_id':None,'titulo_':'PRIVATE_TITLE','status':'unknown','prazo':'invalid'}])
    assert result['materias_com_aluno_invalido']==[9]
    assert result['tarefas_com_materia_invalida']==[11]
    assert result['tarefas_com_status_invalido']==[11]
    assert result['tarefas_com_prazo_invalido']==[11]
    assert 'PRIVATE_' not in json.dumps(result)
    assert module.summarize([{'id':1,'alunos_id':2,'carga_horaria':40}],[{'id':4,'materias_id':1,'status':'em_andamento ','prazo':None}])['tarefas_com_status_invalido']==[]
