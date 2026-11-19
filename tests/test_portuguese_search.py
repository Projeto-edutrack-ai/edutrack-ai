import unicodedata
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.search_text import search_key
from app.models.subject import Subject
from test_adequacao import register,subject,task

client=TestClient(app)

@pytest.mark.parametrize('form',['NFC','NFD'])
@pytest.mark.parametrize('query',['Integração','INTEGRAÇÃO','integracao','integração'])
def test_portuguese_search_matches_composition_case_and_accents_without_cross_user_data(form,query):
    a,user=register();b,_=register()
    stored=unicodedata.normalize(form,'Teste de Integração')
    own=subject(a,stored);foreign=subject(b,stored)
    t=task(a,own['id'],title=stored)
    task(b,foreign['id'],title=stored)
    response=client.get('/api/search',headers=a,params={'q':query})
    assert response.status_code==200,response.text
    data=response.json()
    assert {row['id'] for row in data['subjects']}=={own['id']}
    assert {row['id'] for row in data['tasks']}=={t['id']}
    with SessionLocal() as db:assert db.get(Subject,own['id']).name==stored


def test_normalization_does_not_turn_like_literals_into_wildcards():
    a,_=register();item=subject(a,'Integração 100%_literal')
    assert client.get('/api/search',headers=a,params={'q':'%_'}).json()['subjects'][0]['id']==item['id']
    assert client.get('/api/search',headers=a,params={'q':'%_naoexiste'}).json()['total_matches']==0
    assert search_key(None)==''


def test_combining_mark_only_is_not_a_match_all_query():
    a,_=register();subject(a,'Minha matéria')
    assert client.get('/api/search',headers=a,params={'q':'\u0301'}).json()['total_matches']==0
