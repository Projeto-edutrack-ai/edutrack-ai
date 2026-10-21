"""Builders de payload do Xano (apenas biblioteca padrão; sem credenciais reais)."""

_DEFAULT_COURSEWORK = object()


def make_work(wid="W1", title="Lista 1", **extra):
    work = {
        "google_coursework_id": wid,
        "title": title,
        "description": "Exercícios do capítulo 1",
        "alternate_link": f"https://classroom.google.com/w/{wid}",
        "max_points": 10,
        "due_at": "2026-10-15T23:59:00Z",
        "state": "PUBLISHED",
        "submission": {"state": "NEW", "google_updated_at": None},
    }
    work.update(extra)
    return work


def make_course(cid="C1", name="Cálculo I", coursework=_DEFAULT_COURSEWORK, **extra):
    course = {
        "google_course_id": cid,
        "name": name,
        "description": "Turma de Cálculo",
        "alternate_link": f"https://classroom.google.com/c/{cid}",
        "selected": True,
        "is_active": True,
        "coursework": [make_work()] if coursework is _DEFAULT_COURSEWORK else coursework,
    }
    course.update(extra)
    return course


def make_export(user_id, courses):
    return {"local_user_id": user_id, "courses": courses}
