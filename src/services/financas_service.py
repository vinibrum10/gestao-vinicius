from __future__ import annotations

from datetime import date

from src.calculations import calcular_variacao_saldo
from src.database import execute, fetch_all, fetch_one
from src.services.semanas_service import inicio_semana, fim_semana


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
        """
        INSERT INTO lancamentos_financeiros (data, tipo, categoria, valor, observacoes)
        VALUES (?, 'despesa', ?, ?, NULL)
        """,
        (data_despesa or date.today().isoformat(), categoria.strip() or "Sem categoria", float(valor)),
    )


def listar_despesas_recentes(limite: int = 20) -> list[dict]:
    return fetch_all(
        """
        SELECT data, categoria, valor
        FROM lancamentos_financeiros
        WHERE tipo = 'despesa'
        ORDER BY data DESC, id DESC
        LIMIT ?
        """,
        (limite,),
    )


def total_despesas_semana(data_inicio: str, data_fim: str) -> float:
    registro = fetch_one(
        """
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM lancamentos_financeiros
        WHERE data BETWEEN ? AND ?
          AND tipo = 'despesa'
        """,
        (data_inicio, data_fim),
    )
    return float(registro["total"] or 0)


def atualizar_caixa_semana(semana_id: int, saldo_atual: float, novo_gasto: float) -> None:
    if novo_gasto > 0:
        registrar_despesa(novo_gasto, "Gasto rápido")

    semana = fetch_one("SELECT data_inicio, data_fim FROM semanas WHERE id = ?", (semana_id,))
    if not semana:
        return

    gasto_acumulado = total_despesas_semana(semana["data_inicio"], semana["data_fim"])
    existente = obter_financas_semana(semana_id) or {}
    salvar_financas(
        semana_id,
        gasto_acumulado,
        saldo_atual,
        existente.get("categoria_mais_pesada") or "Gasto rápido",
        bool(existente.get("teve_gasto_inesperado", False)),
        existente.get("observacoes") or "",
    )


def obter_resumo_orcamento() -> dict:
    inicio_atual = inicio_semana()
    fim_atual = fim_semana(inicio_atual)
    ultimo = fetch_one(
        """
        SELECT fs.saldo_atual, s.data_inicio, s.data_fim
        FROM financas_semanais fs
        JOIN semanas s ON s.id = fs.semana_id
        ORDER BY CASE WHEN s.data_inicio = ? THEN 0 ELSE 1 END, s.data_inicio DESC
        LIMIT 1
        """,
        (inicio_atual.isoformat(),),
    )
    saldo_atual = float(ultimo["saldo_atual"] or 0) if ultimo else 0.0
    gasto_semana = total_despesas_semana(inicio_atual.isoformat(), fim_atual.isoformat())
    return {
        "saldo_atual": saldo_atual,
        "gasto_semana": gasto_semana,
        "margem_livre": saldo_atual - gasto_semana,
    }
