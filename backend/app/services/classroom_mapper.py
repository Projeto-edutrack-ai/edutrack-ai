"""Mapeamento do formato canônico do Xano (Classroom) para o modelo do EduTrack.

Somente biblioteca padrão: não depende de banco, HTTP nem do FastAPI, o que mantém estas
regras fáceis de testar. O contrato do payload está em openspec/specs/xano-classroom-contract.md.

Regras de data: toda data é convertida para UTC e devolvida SEM tzinfo (UTC "ingênuo"), que é
como o SQLite/SQLAlchemy já armazena as datas do projeto. Strings sem fuso são assumidas UTC.
Números são epoch (o Xano emite timestamps em milissegundos); valores >= 1e11 são tratados
como milissegundos e menores como segundos.
"""
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

COMPLETED_SUBMISSION_STATES = frozenset({"TURNED_IN", "RETURNED"})
KNOWN_SUBMISSION_STATES = frozenset(
    {"NEW", "CREATED", "TURNED_IN", "RETURNED", "RECLAIMED_BY_STUDENT", "SUBMISSION_STATE_UNSPECIFIED"}
)
# Atividades nesses estados não são importadas (rascunho não é visível ao aluno; excluída saiu do curso)
SKIPPED_COURSEWORK_STATES = frozenset({"DRAFT", "DELETED"})

_EPOCH_MS_THRESHOLD = 100_000_000_000  # 1e11


class InvalidExportError(ValueError):
    """O payload inteiro é inutilizável (estrutura errada ou pertence a outro usuário)."""


class InvalidItemError(ValueError):
    """Um item específico (curso/atividade/campo) é inválido; o item é descartado."""


# ----------------------------------------------------------------------------- campos simples

def clean_text(value: Any) -> Optional[str]:
    """Texto aparado; vazio/None vira None. Números viram texto (IDs numéricos do Xano)."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise InvalidItemError(f"valor de texto inválido: {value!r}")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise InvalidItemError(f"valor de texto inválido: {value!r}")
        text = str(int(value)) if float(value).is_integer() else str(value)
    elif isinstance(value, str):
        text = value.strip()
    else:
        raise InvalidItemError(f"valor de texto inválido: {type(value).__name__}")
    return text or None


def _require_text(value: Any, label: str) -> str:
    text = clean_text(value)
    if text is None:
        raise InvalidItemError(f"{label} ausente ou vazio")
    return text


def _normalize_fraction(iso: str) -> str:
    """Ajusta frações de segundo para 6 dígitos (compatível com fromisoformat do Python 3.10+)."""
    return re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], iso, count=1)


def parse_xano_datetime(value: Any) -> Optional[datetime]:
    """Converte o valor de data do Xano em datetime UTC sem tzinfo. None/'' -> None; inválido -> erro."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise InvalidItemError(f"data inválida: {value!r}")

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, (int, float)):
        dt = _from_epoch(float(value), value)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if re.fullmatch(r"-?\d+(\.\d+)?", text):
            dt = _from_epoch(float(text), value)
        else:
            iso = text[:-1] + "+00:00" if text[-1] in ("Z", "z") else text
            try:
                dt = datetime.fromisoformat(_normalize_fraction(iso))
            except ValueError as exc:
                raise InvalidItemError(f"data inválida: {value!r}") from exc
    else:
        raise InvalidItemError(f"data inválida: {type(value).__name__}")

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _from_epoch(number: float, original: Any) -> datetime:
    if not math.isfinite(number):
        raise InvalidItemError(f"data inválida: {original!r}")
    seconds = number / 1000.0 if abs(number) >= _EPOCH_MS_THRESHOLD else number
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise InvalidItemError(f"data inválida: {original!r}") from exc


def parse_points(value: Any) -> Optional[float]:
    """Pontuação máxima: None/'' -> None; negativa, NaN/inf ou não numérica -> erro. Arredonda a 2 casas."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise InvalidItemError(f"pontuação inválida: {value!r}")
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    try:
        number = float(Decimal(str(value)))
    except (InvalidOperation, ValueError) as exc:
        raise InvalidItemError(f"pontuação inválida: {value!r}") from exc
    if not math.isfinite(number) or number < 0:
        raise InvalidItemError(f"pontuação inválida: {value!r}")
    return round(number, 2)


def normalize_submission_state(value: Any) -> Optional[str]:
    """Estado em MAIÚSCULAS ou None. Valores desconhecidos são preservados (ver is_known_state)."""
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    text = value.strip().upper()
    return text or None


def is_known_state(state: Optional[str]) -> bool:
    return state is None or state in KNOWN_SUBMISSION_STATES


def is_completed_state(state: Optional[str]) -> bool:
    """Somente TURNED_IN e RETURNED contam como concluído; qualquer outro/desconhecido não."""
    return state in COMPLETED_SUBMISSION_STATES


def initial_status(state: Optional[str]) -> str:
    return "completed" if is_completed_state(state) else "pending"


def resolve_status_on_update(
    current_status: str, previous_state: Optional[str], new_state: Optional[str]
) -> Tuple[str, bool]:
    """Define o status de uma tarefa já existente.

    O Classroom só PROMOVE para 'completed', e apenas quando a entrega passa de não-concluída
    para concluída. Nunca rebaixa, e uma mudança manual do aluno não é refeita a cada sincronização.
    Retorna (status, concluido_agora_pelo_classroom).
    """
    if is_completed_state(new_state) and not is_completed_state(previous_state) and current_status != "completed":
        return "completed", True
    return current_status, False


# ----------------------------------------------------------------------------- estruturas

@dataclass(frozen=True)
class CanonicalCoursework:
    google_coursework_id: str
    title: str
    description: Optional[str]
    link: Optional[str]
    max_points: Optional[float]
    due_at: Optional[datetime]
    state: Optional[str]
    has_submission: bool
    submission_state: Optional[str]
    submission_updated_at: Optional[datetime]


@dataclass(frozen=True)
class CanonicalCourse:
    google_course_id: str
    name: str
    description: Optional[str]
    link: Optional[str]
    coursework: Tuple[CanonicalCoursework, ...] = ()


@dataclass
class ParsedExport:
    courses: List[CanonicalCourse] = field(default_factory=list)
    skipped_courses: int = 0
    skipped_coursework: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ----------------------------------------------------------------------------- parsing

def parse_export(payload: Any, expected_user_id: Optional[int] = None) -> ParsedExport:
    """Valida o payload do Xano e o converte em estruturas tipadas.

    Levanta InvalidExportError se a estrutura geral for inválida ou pertencer a outro usuário.
    Itens individuais inválidos são descartados e registrados em ``errors`` (não derrubam o lote).
    """
    if not isinstance(payload, dict):
        raise InvalidExportError("export do Xano deve ser um objeto JSON")
    raw_courses = payload.get("courses")
    if not isinstance(raw_courses, list):
        raise InvalidExportError("export do Xano sem a lista 'courses'")

    if expected_user_id is not None and payload.get("local_user_id") is not None:
        try:
            received = int(payload["local_user_id"])
        except (TypeError, ValueError) as exc:
            raise InvalidExportError("local_user_id do export é inválido") from exc
        if received != int(expected_user_id):
            raise InvalidExportError("export pertence a outro usuário")

    parsed = ParsedExport()
    seen_courses = set()

    for ci, raw in enumerate(raw_courses):
        label = f"courses[{ci}]"
        if not isinstance(raw, dict):
            parsed.errors.append(f"{label}: item inválido")
            continue
        if raw.get("selected") is False or raw.get("is_active") is False:
            parsed.skipped_courses += 1
            continue
        try:
            course_id = _require_text(raw.get("google_course_id"), "google_course_id")
            name = _require_text(raw.get("name"), "name")
            description = clean_text(raw.get("description")) or clean_text(raw.get("description_heading"))
            link = clean_text(raw.get("alternate_link"))
        except InvalidItemError as exc:
            parsed.errors.append(f"{label}: {exc}")
            continue
        if course_id in seen_courses:
            parsed.warnings.append(f"{label}: curso {course_id} repetido no export; ignorado")
            continue
        seen_courses.add(course_id)

        coursework: List[CanonicalCoursework] = []
        raw_work = raw.get("coursework")
        if raw_work is None:
            raw_work = []
        elif not isinstance(raw_work, list):
            parsed.errors.append(f"{label}.coursework: deve ser uma lista")
            raw_work = []

        seen_work = set()
        for wi, item in enumerate(raw_work):
            wlabel = f"{label}.coursework[{wi}]"
            if not isinstance(item, dict):
                parsed.errors.append(f"{wlabel}: item inválido")
                continue
            work_state = normalize_submission_state(item.get("state"))
            if item.get("is_active") is False or work_state in SKIPPED_COURSEWORK_STATES:
                parsed.skipped_coursework += 1
                continue
            try:
                work = _parse_coursework(item, parsed, wlabel)
            except InvalidItemError as exc:
                parsed.errors.append(f"{wlabel}: {exc}")
                continue
            if work.google_coursework_id in seen_work:
                parsed.warnings.append(f"{wlabel}: atividade {work.google_coursework_id} repetida; ignorada")
                continue
            seen_work.add(work.google_coursework_id)
            coursework.append(work)

        parsed.courses.append(
            CanonicalCourse(
                google_course_id=course_id,
                name=name,
                description=description,
                link=link,
                coursework=tuple(coursework),
            )
        )
    return parsed


def _parse_coursework(item: Dict[str, Any], parsed: ParsedExport, label: str) -> CanonicalCoursework:
    submission = item.get("submission")
    has_submission = isinstance(submission, dict)
    submission_state = None
    submission_updated = None
    if has_submission:
        submission_state = normalize_submission_state(submission.get("state"))
        if not is_known_state(submission_state):
            parsed.warnings.append(f"{label}: estado de entrega desconhecido '{submission_state}' (tratado como não concluído)")
        submission_updated = parse_xano_datetime(submission.get("google_updated_at"))
    return CanonicalCoursework(
        google_coursework_id=_require_text(item.get("google_coursework_id"), "google_coursework_id"),
        title=_require_text(item.get("title"), "title"),
        description=clean_text(item.get("description")),
        link=clean_text(item.get("alternate_link")),
        max_points=parse_points(item.get("max_points")),
        due_at=parse_xano_datetime(item.get("due_at")),
        state=normalize_submission_state(item.get("state")),
        has_submission=has_submission,
        submission_state=submission_state,
        submission_updated_at=submission_updated,
    )


# ----------------------------------------------------------------------------- mapeamento

def subject_values(course: CanonicalCourse) -> Dict[str, Any]:
    """Campos de Subject controlados pelo Classroom (workload_hours etc. ficam locais)."""
    return {
        "name": course.name,
        "description": course.description,
        "classroom_link": course.link,
    }


def task_values(work: CanonicalCoursework) -> Dict[str, Any]:
    """Campos de AcademicTask controlados pelo Classroom (due_at -> due_date, max_points, link)."""
    return {
        "title": work.title,
        "description": work.description,
        "due_date": work.due_at,
        "max_points": work.max_points,
        "classroom_link": work.link,
    }
