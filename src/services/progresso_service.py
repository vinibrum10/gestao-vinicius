from __future__ import annotations

from src.database import execute, fetch_all
from src.services.frentes_service import registrar_acao_frente


def registrar_progresso(semana_id: int, frente_id: int, minutos: int, resumo: str, data_acao: str) -> int:
    registrar_acao_frente(frente_id, data_acao)
    return execute(
        """
        INSERT INTO progresso (semana_id, frente_id, minutos_realizados, resumo_acao, data_acao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (semana_id, frente_id, minutos, resumo, data_acao),
    )


def listar_progresso(semana_id: int | None = None) -> list[dict]:
    query = """
        SELECT p.*, s.data_inicio, f.nome AS frente
        FROM progresso p
        JOIN semanas s ON s.id = p.semana_id
        JOIN frentes f ON f.id = p.frente_id
        WHERE 1 = 1
    """
    params = []
    if semana_id:
        query += " AND p.semana_id = ?"
        params.append(semana_id)
    query += " ORDER BY p.data_acao DESC"
    return fetch_all(query, params)


def tarefas_concluidas_por_semana() -> list[dict]:
    return fetch_all(
        """
        SELECT s.data_inicio, COUNT(t.id) AS tarefas_concluidas
        FROM semanas s
        LEFT JOIN tarefas t ON t.semana_id = s.id AND t.status = 'concluída'
        GROUP BY s.id
        ORDER BY s.data_inicio
        """
    )


def tempo_por_frente() -> list[dict]:
    return fetch_all(
        """
        SELECT f.nome AS frente, COALESCE(SUM(p.minutos_realizados), 0) AS minutos_realizados
        FROM frentes f
        LEFT JOIN progresso p ON p.frente_id = f.id
        GROUP BY f.id
        ORDER BY minutos_realizados DESC
        """
    )
