"""Testes da sincronização Xano -> SQLite com Xano mockado (sem credenciais reais)."""
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User
from app.services.classroom_sync import ClassroomSyncError, sync_user_from_xano
from app.services.xano_client import (
    XanoHTTPError, XanoInvalidResponseError, XanoTimeoutError, XanoConnectionError,
)
from classroom_fakes import FakeXano
from classroom_helpers import make_course, make_export, make_work


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def users(db):
    created = [User(name=n, email=f"{n.lower()}@x.com", password_hash="h") for n in ("Ana", "Bruno")]
    db.add_all(created)
    db.commit()
    return created


@pytest.fixture()
def xano():
    return FakeXano()


def counts(db):
    return db.query(Subject).count(), db.query(AcademicTask).count()


def sync(db, xano, user):
    return sync_user_from_xano(db, user.id, xano.client())


def one_course_export(user, **work_extra):
    return make_export(user.id, [make_course(coursework=[make_work(**work_extra)])])


# ----------------------------------------------------------------------------- importação

def test_primeiro_import(db, users, xano):
    ana = users[0]
    done = make_work("W2", "Prova", submission={"state": "TURNED_IN", "google_updated_at": "2026-10-10T12:00:00Z"})
    xano.exports[ana.id] = make_export(ana.id, [
        make_course("C1", "Cálculo I", [make_work("W1", "Lista 1"), done]),
        make_course("C2", "Física", [make_work("W3", "Relatório", max_points=2.5)]),
    ])
    result = sync(db, xano, ana)

    assert (result.courses_created, result.tasks_created) == (2, 3)
    assert counts(db) == (2, 3)
    subject = db.query(Subject).filter_by(classroom_course_id="C1").one()
    assert (subject.user_id, subject.source, subject.name) == (ana.id, "classroom", "Cálculo I")
    assert subject.workload_hours == 60.0 and subject.classroom_link.endswith("/c/C1")

    t1 = db.query(AcademicTask).filter_by(classroom_coursework_id="W1").one()
    assert t1.subject_id == subject.id and t1.source == "classroom"
    assert t1.due_date == datetime(2026, 10, 15, 23, 59) and t1.max_points == 10.0
    assert t1.classroom_link.endswith("/w/W1") and t1.status == "pending" and t1.completed_at is None
    assert (t1.estimated_time_minutes, t1.actual_time_minutes) == (60.0, 0.0)

    t2 = db.query(AcademicTask).filter_by(classroom_coursework_id="W2").one()
    assert t2.status == "completed" and t2.completed_at == datetime(2026, 10, 10, 12, 0)
    assert t2.classroom_submission_state == "TURNED_IN" and result.tasks_completed_by_classroom == 1
    assert xano.calls[0].url.params["local_user_id"] == str(ana.id)


def test_segundo_import_nao_duplica(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[make_work("W1"), make_work("W2")])])
    sync(db, xano, ana)
    before = counts(db)
    ids_before = sorted(t.id for t in db.query(AcademicTask))

    second = sync(db, xano, ana)
    assert counts(db) == before == (1, 2)
    assert sorted(t.id for t in db.query(AcademicTask)) == ids_before
    assert (second.courses_created, second.tasks_created) == (0, 0)
    assert (second.courses_unchanged, second.tasks_unchanged) == (1, 2)
    assert (second.courses_updated, second.tasks_updated) == (0, 0)
    sync(db, xano, ana)
    assert counts(db) == before


def test_atualiza_atividade_existente(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana)
    sync(db, xano, ana)
    task_id = db.query(AcademicTask).one().id

    xano.exports[ana.id] = one_course_export(ana, title="Lista 1 (revisada)", description="Novo enunciado",
                                             alternate_link="https://classroom.google.com/w/novo")
    result = sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    assert task.id == task_id and counts(db) == (1, 1)
    assert (task.title, task.description) == ("Lista 1 (revisada)", "Novo enunciado")
    assert task.classroom_link.endswith("/w/novo") and result.tasks_updated == 1


def test_alteracao_de_prazo(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana)
    sync(db, xano, ana)
    xano.exports[ana.id] = one_course_export(ana, due_at="2026-11-01T02:00:00-03:00")
    result = sync(db, xano, ana)
    assert db.query(AcademicTask).one().due_date == datetime(2026, 11, 1, 5, 0)
    assert result.tasks_updated == 1
    xano.exports[ana.id] = one_course_export(ana, due_at=None)  # prazo removido no Classroom
    sync(db, xano, ana)
    assert db.query(AcademicTask).one().due_date is None


def test_alteracao_de_pontuacao(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana, max_points=10)
    sync(db, xano, ana)
    xano.exports[ana.id] = one_course_export(ana, max_points=7.5)
    result = sync(db, xano, ana)
    assert db.query(AcademicTask).one().max_points == 7.5 and result.tasks_updated == 1


def test_atualiza_nome_do_curso(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", "Cálculo I", [])])
    sync(db, xano, ana)
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", "Cálculo Diferencial", [])])
    result = sync(db, xano, ana)
    assert db.query(Subject).one().name == "Cálculo Diferencial" and result.courses_updated == 1


# ----------------------------------------------------------------------------- campos locais

def test_preserva_campos_locais(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana)
    sync(db, xano, ana)

    subject = db.query(Subject).one()
    subject.workload_hours, subject.professor = 90.0, "Profa. Marta"
    subject.start_date = datetime(2026, 2, 1)
    task = db.query(AcademicTask).one()
    task.actual_time_minutes, task.estimated_time_minutes, task.status = 95.0, 120.0, "in_progress"
    db.commit()

    xano.exports[ana.id] = one_course_export(ana, title="Novo título", max_points=20, due_at="2026-12-01T00:00:00Z")
    sync(db, xano, ana)

    subject, task = db.query(Subject).one(), db.query(AcademicTask).one()
    assert (subject.workload_hours, subject.professor, subject.start_date) == (90.0, "Profa. Marta", datetime(2026, 2, 1))
    assert (task.actual_time_minutes, task.estimated_time_minutes, task.status) == (95.0, 120.0, "in_progress")
    assert (task.title, task.max_points) == ("Novo título", 20.0)  # campos do Classroom atualizados


def test_status_concluido_pelo_classroom_e_reabertura_manual(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana, submission={"state": "NEW"})
    sync(db, xano, ana)
    assert db.query(AcademicTask).one().status == "pending"

    turned_in = {"state": "TURNED_IN", "google_updated_at": "2026-10-12T10:00:00Z"}
    xano.exports[ana.id] = one_course_export(ana, submission=turned_in)
    result = sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    assert (task.status, task.completed_at, result.tasks_completed_by_classroom) == (
        "completed", datetime(2026, 10, 12, 10, 0), 1)

    task.status, task.completed_at = "pending", None  # o aluno reabre manualmente
    db.commit()
    sync(db, xano, ana)  # mesmo estado no Classroom: não desfaz a escolha do aluno
    assert db.query(AcademicTask).one().status == "pending"

    xano.exports[ana.id] = one_course_export(ana, submission={"state": "RECLAIMED_BY_STUDENT"})
    sync(db, xano, ana)  # o Classroom nunca rebaixa nem conclui nesse caso
    assert db.query(AcademicTask).one().status == "pending"


def test_classroom_nao_rebaixa_tarefa_concluida_manualmente(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana, submission={"state": "NEW"})
    sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    task.status, task.completed_at = "completed", datetime(2026, 10, 1)
    db.commit()
    xano.exports[ana.id] = one_course_export(ana, submission={"state": "TURNED_IN"})
    result = sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    assert task.status == "completed" and task.completed_at == datetime(2026, 10, 1)
    assert result.tasks_completed_by_classroom == 0


def test_nao_toca_nem_apaga_registros_locais(db, users, xano):
    ana = users[0]
    local = Subject(user_id=ana.id, name="Cálculo I", professor="Local", workload_hours=45.0)
    db.add(local)
    db.flush()
    db.add(AcademicTask(user_id=ana.id, subject_id=local.id, title="Lista 1", status="in_progress",
                        estimated_time_minutes=30.0, actual_time_minutes=10.0))
    db.commit()

    xano.exports[ana.id] = one_course_export(ana)  # mesmo nome de curso e título que os locais
    sync(db, xano, ana)
    assert counts(db) == (2, 2)  # sem adoção automática por nome: nada de mesclar/duplicar o local
    local = db.query(Subject).filter_by(id=local.id).one()
    assert (local.source, local.classroom_course_id, local.professor, local.workload_hours) == ("local", None, "Local", 45.0)
    task = db.query(AcademicTask).filter_by(subject_id=local.id).one()
    assert (task.source, task.status, task.actual_time_minutes) == ("local", "in_progress", 10.0)


def test_nao_apaga_o_que_sumiu_do_classroom(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[make_work("W1"), make_work("W2")]),
                                                make_course("C2", coursework=[make_work("W3")])])
    sync(db, xano, ana)
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[make_work("W1")])])
    sync(db, xano, ana)
    assert counts(db) == (2, 3)


# ----------------------------------------------------------------------------- isolamento

def test_isolamento_entre_usuarios(db, users, xano):
    ana, bruno = users
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", "Cálculo Ana", [make_work("W1", "Ana 1")])])
    xano.exports[bruno.id] = make_export(bruno.id, [make_course("C1", "Cálculo Bruno", [make_work("W1", "Bruno 1")])])
    sync(db, xano, ana)
    sync(db, xano, bruno)

    assert counts(db) == (2, 2)  # mesmos IDs do Classroom, usuários diferentes: sem colisão
    for user, name, title in ((ana, "Cálculo Ana", "Ana 1"), (bruno, "Cálculo Bruno", "Bruno 1")):
        assert db.query(Subject).filter_by(user_id=user.id).one().name == name
        assert db.query(AcademicTask).filter_by(user_id=user.id).one().title == title
    assert [c.url.params["local_user_id"] for c in xano.calls] == [str(ana.id), str(bruno.id)]

    xano.exports[bruno.id] = make_export(bruno.id, [make_course("C1", "Bruno mudou", [make_work("W1", "Bruno 2")])])
    sync(db, xano, bruno)
    assert db.query(Subject).filter_by(user_id=ana.id).one().name == "Cálculo Ana"
    assert db.query(AcademicTask).filter_by(user_id=ana.id).one().title == "Ana 1"


def test_export_de_outro_usuario_e_rejeitado(db, users, xano):
    ana, bruno = users
    xano.exports[ana.id] = make_export(bruno.id, [make_course()])  # payload do usuário errado
    with pytest.raises(XanoInvalidResponseError):
        sync(db, xano, ana)
    assert counts(db) == (0, 0)


def test_indice_unico_impede_duplicata_no_banco(db, users):
    ana = users[0]
    db.add(Subject(user_id=ana.id, name="A", classroom_course_id="C1"))
    db.commit()
    db.add(Subject(user_id=ana.id, name="B", classroom_course_id="C1"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.add_all([Subject(user_id=ana.id, name="L1"), Subject(user_id=ana.id, name="L2")])  # locais: NULLs não colidem
    db.commit()


# ----------------------------------------------------------------------------- dados limite

def test_curso_sem_atividades(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[]), make_course("C2", coursework=None)])
    result = sync(db, xano, ana)
    assert counts(db) == (2, 0) and result.courses_created == 2 and result.errors == []
    sync(db, xano, ana)
    assert counts(db) == (2, 0)


def test_export_vazio(db, users, xano):
    result = sync(db, xano, users[0])
    assert counts(db) == (0, 0) and result.errors == []


def test_dados_incompletos_e_nulos(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[
        {"google_coursework_id": "W1", "title": "Mínima"},                       # só o essencial
        make_work("W2", "Nulos", description=None, max_points=None, due_at=None, alternate_link=None, submission=None),
        make_work("W3", title=""),                                                # inválida: sem título
        make_work("W4", due_at="data errada"),                                    # inválida: data
        make_work("W5", max_points="abc"),                                        # inválida: pontuação
        make_work("W6", state="DRAFT"),                                           # rascunho: ignorada
        {"title": "sem id"},                                                      # inválida: sem ID
    ])])
    result = sync(db, xano, ana)
    assert counts(db) == (1, 2)
    minimal = db.query(AcademicTask).filter_by(classroom_coursework_id="W1").one()
    assert (minimal.description, minimal.due_date, minimal.max_points, minimal.classroom_link) == (None, None, None, None)
    assert minimal.status == "pending" and minimal.classroom_submission_state is None
    assert len(result.errors) == 4 and result.skipped_coursework == 1


def test_sem_dados_de_entrega_nao_apaga_estado_anterior(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana, submission={"state": "TURNED_IN"})
    sync(db, xano, ana)
    xano.exports[ana.id] = one_course_export(ana, submission=None)
    sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    assert (task.classroom_submission_state, task.status) == ("TURNED_IN", "completed")


def test_estado_desconhecido_nao_conclui_e_gera_aviso(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana, submission={"state": "ESTADO_NOVO"})
    result = sync(db, xano, ana)
    task = db.query(AcademicTask).one()
    assert (task.status, task.classroom_submission_state) == ("pending", "ESTADO_NOVO")
    assert any("ESTADO_NOVO" in w for w in result.warnings)


# ----------------------------------------------------------------------------- falhas

def test_erros_do_xano_nao_alteram_o_banco(db, users, xano):
    ana = users[0]
    xano.exports[ana.id] = one_course_export(ana)
    sync(db, xano, ana)
    before = counts(db)
    snapshot = db.query(AcademicTask).one().title

    xano.exports[ana.id] = one_course_export(ana, title="NÃO DEVE APARECER")
    for mode, exc in (("500", XanoHTTPError), ("401", XanoHTTPError),
                      ("timeout", XanoTimeoutError), ("connect", XanoConnectionError)):
        xano.mode = mode
        with pytest.raises(exc):
            sync(db, xano, ana)
    assert counts(db) == before
    assert db.query(AcademicTask).one().title == snapshot


def test_resposta_invalida_do_xano_nao_altera_o_banco(db, users, xano):
    ana = users[0]
    for mode in ("not_json", "list", "no_courses"):
        xano.mode = mode
        with pytest.raises(XanoInvalidResponseError):
            sync(db, xano, ana)
    assert counts(db) == (0, 0)


def test_falha_de_banco_faz_rollback_total(db, users, xano, monkeypatch):
    ana = users[0]
    xano.exports[ana.id] = make_export(ana.id, [make_course("C1", coursework=[make_work("W1")])])

    def boom():
        raise SQLAlchemyError("disco cheio")
    monkeypatch.setattr(db, "commit", boom)
    with pytest.raises(ClassroomSyncError):
        sync(db, xano, ana)
    monkeypatch.undo()
    assert counts(db) == (0, 0)
