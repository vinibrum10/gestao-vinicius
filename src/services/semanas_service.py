from __future__ import annotations

from datetime import date, timedelta

from src.database import execute, fetch_all, fetch_one

PESOS_SEMANA = ["leve", "moderada", "pesada", "muito pesada"]


def normalizar_peso_semana(peso_semana: str | None) -> str:
    if peso_semana == "normal":
        return "moderada"
    if peso_semana in PESOS_SEMANA:
        return peso_semana
    return "moderada"


def inicio_semana(data_ref: date | None = None) -> date:
    data_ref = data_ref or date.today()
    return data_ref - timedelta(days=data_ref.weekday())


def fim_semana(data_inicio: date) -> date:
    return data_inicio + timedelta(days=6)


def listar_semanas() -> list[dict]:
    semanas = fetch_all(
        """
        SELECT s.*, f.nome AS foco_principal
        FROM semanas s
        LEFT JOIN frentes f ON f.id = s.foco_principal_frente_id
        ORDER BY s.data_inicio DESC
        """
    )
    for semana in semanas:
        semana["peso_semana"] = normalizar_peso_semana(semana.get("peso_semana"))
    return semanas


def obter_semana_atual() -> dict | None:
    inicio = inicio_semana().isoformat()
    semana = fetch_one("SELECT * FROM semanas WHERE data_inicio = ?", (inicio,))
    if semana:
        semana["peso_semana"] = normalizar_peso_semana(semana.get("peso_semana"))
    return semana


def obter_semana(semana_id: int) -> dict | None:
    semana = fetch_one("SELECT * FROM semanas WHERE id = ?", (semana_id,))
    if semana:
        semana["peso_semana"] = normalizar_peso_semana(semana.get("peso_semana"))
    return semana


def criar_ou_atualizar_semana(
    data_inicio: str,
    foco_principal_frente_id: int | None,
    tempo_livre_estimado_horas: float,
    tempo_livre_util_horas: float,
    peso_semana: str,
    observacoes: str,
) -> int:
    data_fim = fim_semana(date.fromisoformat(data_inicio)).isoformat()
    peso_semana = normalizar_peso_semana(peso_semana)
    existente = fetch_one("SELECT id FROM semanas WHERE data_inicio = ?", (data_inicio,))
    if existente:
        execute(
            """
            UPDATE semanas
            SET data_fim = ?, foco_principal_frente_id = ?, tempo_livre_estimado_horas = ?,
                tempo_livre_util_horas = ?, peso_semana = ?, observacoes = ?,
                atualizada_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (data_fim, foco_principal_frente_id, tempo_livre_estimado_horas, tempo_livre_util_horas, peso_semana, observacoes, existente["id"]),
        )
        return int(existente["id"])
    return execute(
        """
        INSERT INTO semanas
        (data_inicio, data_fim, foco_principal_frente_id, tempo_livre_estimado_horas,
         tempo_livre_util_horas, peso_semana, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (data_inicio, data_fim, foco_principal_frente_id, tempo_livre_estimado_horas, tempo_livre_util_horas, peso_semana, observacoes),
    )
