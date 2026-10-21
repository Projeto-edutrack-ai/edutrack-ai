"""Testes do mapeamento Xano -> EduTrack (somente regras puras: datas, pontuação, estados, parsing)."""
from datetime import datetime

import pytest

from app.services import classroom_mapper as m
from classroom_helpers import make_course, make_export, make_work


# ----------------------------------------------------------------------------- datas / timezone

def test_iso_utc_z_e_offset_viram_utc_naive():
    expected = datetime(2026, 10, 15, 23, 59, 0)
    assert m.parse_xano_datetime("2026-10-15T23:59:00Z") == expected
    assert m.parse_xano_datetime("2026-10-15T23:59:00+00:00") == expected
    assert m.parse_xano_datetime("2026-10-15T20:59:00-03:00") == expected  # fuso convertido para UTC
    assert m.parse_xano_datetime("2026-10-16T02:59:00+03:00") == datetime(2026, 10, 15, 23, 59, 0)


def test_iso_sem_fuso_assume_utc_e_fracao_de_segundos():
    assert m.parse_xano_datetime("2026-10-15T23:59:00") == datetime(2026, 10, 15, 23, 59, 0)
    assert m.parse_xano_datetime("2026-10-15T23:59:00.5Z") == datetime(2026, 10, 15, 23, 59, 0, 500000)
    assert m.parse_xano_datetime("2026-10-15T23:59:00.123456789Z").microsecond == 123456


def test_epoch_em_milissegundos_e_segundos():
    ms = 1_760_572_740_000  # 2025-10-15T23:59:00Z
    assert m.parse_xano_datetime(ms) == datetime(2025, 10, 15, 23, 59, 0)
    assert m.parse_xano_datetime(str(ms)) == datetime(2025, 10, 15, 23, 59, 0)
    assert m.parse_xano_datetime(ms // 1000) == datetime(2025, 10, 15, 23, 59, 0)


def test_datetime_aware_e_convertido_e_nulos_viram_none():
    from datetime import timezone, timedelta
    aware = datetime(2026, 10, 15, 20, 59, tzinfo=timezone(timedelta(hours=-3)))
    assert m.parse_xano_datetime(aware) == datetime(2026, 10, 15, 23, 59)
    for empty in (None, "", "   "):
        assert m.parse_xano_datetime(empty) is None


def test_datas_invalidas_levantam_erro():
    for bad in ("amanhã", "2026-13-45", True, [], {}, float("nan"), float("inf"), 10**30):
        with pytest.raises(m.InvalidItemError):
            m.parse_xano_datetime(bad)


# ----------------------------------------------------------------------------- pontuação

def test_pontuacao_valida_e_nula():
    assert m.parse_points(10) == 10.0
    assert m.parse_points("7.5") == 7.5
    assert m.parse_points(8.456) == 8.46
    assert m.parse_points(0) == 0.0
    for empty in (None, "", "  "):
        assert m.parse_points(empty) is None


def test_pontuacao_invalida_levanta_erro():
    for bad in (-1, "-3", "dez", True, float("nan"), float("inf"), [], {}):
        with pytest.raises(m.InvalidItemError):
            m.parse_points(bad)


# ----------------------------------------------------------------------------- estados da entrega

def test_estados_concluidos_e_desconhecidos():
    assert m.is_completed_state("TURNED_IN") and m.is_completed_state("RETURNED")
    for state in ("NEW", "CREATED", "RECLAIMED_BY_STUDENT", "ALGO_NOVO", None):
        assert not m.is_completed_state(state)
    assert m.normalize_submission_state(" turned_in ") == "TURNED_IN"
    assert m.normalize_submission_state("") is None and m.normalize_submission_state(5) is None
    assert m.is_known_state("NEW") and m.is_known_state(None) and not m.is_known_state("ALGO_NOVO")
    assert m.initial_status("RETURNED") == "completed" and m.initial_status("NEW") == "pending"


def test_status_so_promove_na_transicao_e_nunca_rebaixa():
    assert m.resolve_status_on_update("pending", "NEW", "TURNED_IN") == ("completed", True)
    assert m.resolve_status_on_update("in_progress", None, "RETURNED") == ("completed", True)
    assert m.resolve_status_on_update("completed", "NEW", "TURNED_IN") == ("completed", False)
    # reabertura manual não é desfeita enquanto o estado do Classroom não muda
    assert m.resolve_status_on_update("pending", "TURNED_IN", "TURNED_IN") == ("pending", False)
    # rebaixamento no Classroom não altera o status local
    assert m.resolve_status_on_update("completed", "TURNED_IN", "RECLAIMED_BY_STUDENT") == ("completed", False)


# ----------------------------------------------------------------------------- parse_export

def test_parse_export_completo():
    work = make_work(submission={"state": "turned_in", "google_updated_at": "2026-10-10T12:00:00Z"})
    parsed = m.parse_export(make_export(1, [make_course(coursework=[work])]), expected_user_id=1)
    assert parsed.errors == [] and parsed.warnings == []
    course = parsed.courses[0]
    assert (course.google_course_id, course.name) == ("C1", "Cálculo I")
    task = course.coursework[0]
    assert task.due_at == datetime(2026, 10, 15, 23, 59) and task.max_points == 10.0
    assert task.submission_state == "TURNED_IN" and task.submission_updated_at == datetime(2026, 10, 10, 12, 0)
    assert m.task_values(task)["due_date"] == task.due_at
    assert m.subject_values(course)["name"] == "Cálculo I"


def test_parse_export_estrutura_invalida():
    for bad in (None, [], "x", {"foo": 1}, {"courses": None}, {"courses": {}}):
        with pytest.raises(m.InvalidExportError):
            m.parse_export(bad)


def test_parse_export_de_outro_usuario_e_rejeitado():
    with pytest.raises(m.InvalidExportError):
        m.parse_export(make_export(2, [make_course()]), expected_user_id=1)
    with pytest.raises(m.InvalidExportError):
        m.parse_export({"local_user_id": "abc", "courses": []}, expected_user_id=1)
    # sem local_user_id no payload: aceito (a checagem é opcional)
    assert m.parse_export({"courses": []}, expected_user_id=1).courses == []


def test_parse_export_dados_nulos_e_incompletos():
    minimal = {"google_coursework_id": 99, "title": "  Só o essencial  "}  # ID numérico vira texto
    course = {"google_course_id": "C9", "name": "Curso", "coursework": None}
    parsed = m.parse_export({"courses": [course, make_course("C8", coursework=[minimal])]})
    assert parsed.errors == []
    assert parsed.courses[0].coursework == ()
    task = parsed.courses[1].coursework[0]
    assert task.google_coursework_id == "99" and task.title == "Só o essencial"
    assert (task.description, task.link, task.max_points, task.due_at) == (None, None, None, None)
    assert task.has_submission is False and task.submission_state is None


def test_parse_export_descarta_itens_invalidos_sem_derrubar_o_lote():
    bad_work = [
        make_work("W1", "Ok"),
        make_work("W2", title=""),                       # sem título
        make_work("W3", due_at="amanhã"),                # data inválida
        make_work("W4", max_points=-5),                  # pontuação inválida
        {"title": "sem id"},                             # sem ID
        "lixo",                                          # item não-objeto
        make_work("W1", "Repetida"),                     # repetida
        make_work("W5", state="DRAFT"),                  # rascunho: ignorada
        make_work("W6", state="deleted"),                # excluída: ignorada
        make_work("W7", is_active=False),                # inativa: ignorada
    ]
    courses = [
        make_course("C1", coursework=bad_work),
        make_course("C2", name=""),                      # sem nome
        {"name": "sem id"},                              # sem ID
        "lixo",
        make_course("C3", selected=False),               # não selecionado
        make_course("C4", is_active=False),
        make_course("C1", name="Repetido"),
    ]
    parsed = m.parse_export({"courses": courses})
    assert [c.google_course_id for c in parsed.courses] == ["C1"]
    assert [w.google_coursework_id for w in parsed.courses[0].coursework] == ["W1"]
    assert parsed.skipped_courses == 2 and parsed.skipped_coursework == 3
    assert len(parsed.errors) == 8 and len(parsed.warnings) == 2


def test_estado_desconhecido_gera_aviso_e_nao_conclui():
    work = make_work(submission={"state": "ALGO_NOVO"})
    parsed = m.parse_export({"courses": [make_course(coursework=[work])]})
    task = parsed.courses[0].coursework[0]
    assert task.submission_state == "ALGO_NOVO" and not m.is_completed_state(task.submission_state)
    assert any("ALGO_NOVO" in w for w in parsed.warnings)


def test_descricao_do_curso_usa_heading_como_fallback():
    c = make_course(description=None, description_heading="Turma A")
    assert m.parse_export({"courses": [c]}).courses[0].description == "Turma A"
