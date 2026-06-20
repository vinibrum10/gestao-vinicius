from __future__ import annotations

from src.calculations import calcular_variacao_saldo
from src.database import execute, fetch_all, fetch_one


def obter_financas_semana(semana_id: int) -> dict | None:
    return fetch_one("SELECT * FROM financas_semanais WHERE semana_id = ?", (semana_id,))


def salvar_financas(semana_id: int, gasto: float, saldo: float, categoria: str, inesperado: bool, observacoes: str) -> int:
    existente = obter_financas_semana(semana_id)
    if existente:
        execute(
            """
            UPDATE financas_semanais
            SET gasto_semana = ?, saldo_atual = ?, categoria_mais_pesada = ?,
                teve_gasto_inesperado = ?, observacoes = ?
            WHERE semana_id = ?
            """,
            (gasto, saldo, categoria, int(inesperado), observacoes, semana_id),
        )
        return int(existente["id"])
    return execute(
        """
        INSERT INTO financas_semanais
        (semana_id, gasto_semana, saldo_atual, categoria_mais_pesada, teve_gasto_inesperado, observacoes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (semana_id, gasto, saldo, categoria, int(inesperado), observacoes),
    )


def listar_historico_financeiro() -> list[dict]:
    registros = fetch_all(
        """
        SELECT fs.*, s.data_inicio, s.data_fim
        FROM financas_semanais fs
        JOIN semanas s ON s.id = fs.semana_id
        ORDER BY s.data_inicio
        """
    )
    saldo_anterior = None
    for item in registros:
        item["variacao_saldo"] = calcular_variacao_saldo(item.get("saldo_atual"), saldo_anterior)
        saldo_anterior = item.get("saldo_atual")
    return registros
