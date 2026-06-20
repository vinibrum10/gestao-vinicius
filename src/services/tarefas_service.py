from __future__ import annotations

from datetime import date

from src.database import execute, fetch_all
from src.services.frentes_service import registrar_acao_frente

STATUS_TAREFAS = ["pendente", "em andamento", "concluída", "pausada", "cancelada"]
PRIORIDADES = ["alta", "média", "baixa"]


def listar_tarefas(semana_id: int | None = None, frente_id: int | None = None, status: str | None = None) -> list[dict]:
    query = """
        SELECT t.*, s.data_inicio, f.nome AS frente
        FROM tarefas t
        JOIN semanas s ON s.id = t.semana_id
        JOIN frentes f ON f.id = t.frente_id
        WHERE 1 = 1
    """
    params: list = []
    if semana_id:
        query += " AND t.semana_id = ?"
        params.append(semana_id)
    if frente_id:
        query += " AND t.frente_id = ?"
        params.append(frente_id)
    if status and status != "todos":
        query += " AND t.status = ?"
        params.append(status)
    query += " ORDER BY s.data_inicio DESC, t.prioridade, t.data_planejada"
    return fetch_all(query, params)


def criar_tarefa(semana_id: int, frente_id: int, titulo: str, descricao: str, tempo: int, data_planejada: str | None, prioridade: str) -> int:
    return execute(
        """
        INSERT INTO tarefas
        (semana_id, frente_id, titulo, descricao, tempo_estimado_minutos, data_planejada, prioridade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (semana_id, frente_id, titulo, descricao, tempo, data_planejada, prioridade),
    )


def atualizar_status_tarefa(tarefa_id: int, status: str, frente_id: int | None = None) -> None:
    concluida_em = date.today().isoformat() if status == "concluída" else None
    execute(
        """
        UPDATE tarefas
        SET status = ?, concluida_em = ?, atualizada_em = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, concluida_em, tarefa_id),
    )
    if status == "concluída" and frente_id:
        registrar_acao_frente(frente_id)
