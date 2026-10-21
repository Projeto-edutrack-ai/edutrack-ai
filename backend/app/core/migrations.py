"""Migração aditiva e idempotente para SQLite (colunas de origem Google Classroom).

Por que existe: ``Base.metadata.create_all`` só cria tabelas ausentes; não adiciona colunas
nem índices a tabelas existentes. Este módulo apenas ADICIONA colunas/índices que faltam.
Nunca remove, renomeia nem reescreve dados. Rodar várias vezes é seguro.

``plan_migration`` é uma função pura (sem banco) para facilitar o teste; ``run_migrations``
lê o estado do banco, pede o plano e executa os comandos.
"""
from typing import Dict, Iterable, List, Mapping, Tuple

from sqlalchemy import text

# tabela -> [(coluna, tipo/DDL SQLite)]. Colunas NOT NULL exigem DEFAULT constante no SQLite.
COLUMN_MIGRATIONS: Dict[str, List[Tuple[str, str]]] = {
    "subjects": [
        ("source", "VARCHAR NOT NULL DEFAULT 'local'"),
        ("classroom_course_id", "VARCHAR"),
        ("classroom_link", "VARCHAR"),
        ("classroom_synced_at", "DATETIME"),
    ],
    "academic_tasks": [
        ("source", "VARCHAR NOT NULL DEFAULT 'local'"),
        ("classroom_coursework_id", "VARCHAR"),
        ("classroom_link", "VARCHAR"),
        ("max_points", "FLOAT"),
        ("classroom_submission_state", "VARCHAR"),
        ("classroom_synced_at", "DATETIME"),
    ],
}

# (nome do índice, tabela, colunas) — todos únicos. Nomes iguais aos declarados nos modelos.
UNIQUE_INDEXES: List[Tuple[str, str, Tuple[str, ...]]] = [
    ("uq_subjects_user_classroom_course", "subjects", ("user_id", "classroom_course_id")),
    ("uq_tasks_user_subject_coursework", "academic_tasks", ("user_id", "subject_id", "classroom_coursework_id")),
]


def plan_migration(
    existing_columns: Mapping[str, Iterable[str]],
    existing_indexes: Iterable[str],
) -> List[str]:
    """Devolve os comandos SQL necessários. Tabelas ausentes são ignoradas (create_all as cria)."""
    present_indexes = set(existing_indexes)
    statements: List[str] = []
    planned_columns: Dict[str, set] = {}

    for table, columns in COLUMN_MIGRATIONS.items():
        if table not in existing_columns:
            continue
        have = set(existing_columns[table])
        for name, ddl in columns:
            if name not in have:
                statements.append(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
                have.add(name)
        planned_columns[table] = have

    for index_name, table, cols in UNIQUE_INDEXES:
        if table not in planned_columns or index_name in present_indexes:
            continue
        if not set(cols) <= planned_columns[table]:
            continue
        statements.append(
            f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON {table} ({', '.join(cols)})"
        )
    return statements


def run_migrations(engine) -> List[str]:
    """Aplica a migração no banco SQLite. Retorna os comandos executados (lista vazia = nada a fazer)."""
    if engine.dialect.name != "sqlite":
        return []  # migração escrita e validada apenas para SQLite

    with engine.begin() as conn:
        tables = {row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'"))}
        existing_columns = {
            table: [row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))]
            for table in COLUMN_MIGRATIONS
            if table in tables
        }
        existing_indexes = [
            row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type = 'index'"))
        ]
        statements = plan_migration(existing_columns, existing_indexes)
        for statement in statements:
            conn.execute(text(statement))
    return statements
