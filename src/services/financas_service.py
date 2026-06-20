from __future__ import annotations

from datetime import date

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


def registrar_despesa(valor: float, categoria: str, data_despesa: str | None = None) -> int:
    return execute(
        "INSERT INTO despesas (data, valor, categoria) VALUES (?, ?, ?)",
        (data_despesa or date.today().isoformat(), float(valor), categoria.strip() or "Sem categoria"),
    )


def listar_despesas_recentes(limite: int = 20) -> list[dict]:
    return fetch_all(
        """
        SELECT id, data, valor, categoria, criada_em
        FROM despesas
        ORDER BY data DESC, id DESC
        LIMIT ?
        """,
        (limite,),
    )


def total_despesas_semana(data_inicio: str, data_fim: str) -> float:
    registro = fetch_one(
        """
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM despesas
        WHERE data BETWEEN ? AND ?
        """,
        (data_inicio, data_fim),
    )
    return float(registro["total"] or 0)


def obter_resumo_orcamento() -> dict:
    ultimo = fetch_one(
        """
        SELECT fs.saldo_atual, s.data_inicio, s.data_fim
        FROM financas_semanais fs
        JOIN semanas s ON s.id = fs.semana_id
        ORDER BY s.data_inicio DESC
        LIMIT 1
        """
    )
    if not ultimo:
        return {"saldo_atual": 0.0, "gasto_semana": 0.0, "margem_livre": 0.0}

    gasto_semana = total_despesas_semana(ultimo["data_inicio"], ultimo["data_fim"])
    saldo_atual = float(ultimo["saldo_atual"] or 0)
    return {
        "saldo_atual": saldo_atual,
        "gasto_semana": gasto_semana,
        "margem_livre": saldo_atual - gasto_semana,
    }
