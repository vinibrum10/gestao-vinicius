from __future__ import annotations

from src.database import execute, fetch_all

TIPOS_BLOCO = [
    "trabalho",
    "aula",
    "inglês",
    "estudo",
    "foco profundo",
    "compromisso pessoal",
    "descanso",
    "financeiro",
    "outro",
]
NIVEIS_ENERGIA = ["alta", "média", "baixa"]


def criar_bloco(semana_id: int, data: str, hora_inicio: str, hora_fim: str, tipo: str, titulo: str, nivel_energia: str, observacoes: str) -> int:
    return execute(
        """
        INSERT INTO blocos_tempo
        (semana_id, data, hora_inicio, hora_fim, tipo, titulo, nivel_energia, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (semana_id, data, hora_inicio, hora_fim, tipo, titulo, nivel_energia, observacoes),
    )


def listar_blocos(semana_id: int | None = None) -> list[dict]:
    query = """
        SELECT b.*, s.data_inicio
        FROM blocos_tempo b
        JOIN semanas s ON s.id = b.semana_id
        WHERE 1 = 1
    """
    params = []
    if semana_id:
        query += " AND b.semana_id = ?"
        params.append(semana_id)
    query += " ORDER BY b.data, b.hora_inicio"
    return fetch_all(query, params)
