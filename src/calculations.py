from __future__ import annotations

from datetime import date, datetime
from typing import Any


def parse_date(value: str | date | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def calcular_divida_atencao(
    ultima_acao_data: str | date | None,
    limite_alerta_dias: int | None,
    status: str,
    hoje: date | None = None,
) -> dict[str, Any]:
    hoje = hoje or date.today()
    limite = int(limite_alerta_dias or 0)

    if status == "pausada":
        return {"classificacao": "pausada", "dias_sem_acao": None}
    if not ultima_acao_data:
        return {"classificacao": "atenção", "dias_sem_acao": None}
    if limite <= 0:
        return {"classificacao": "ok", "dias_sem_acao": 0}

    dias = (hoje - parse_date(ultima_acao_data)).days
    if dias > limite * 2:
        classificacao = "crítico"
    elif dias > limite:
        classificacao = "atenção"
    else:
        classificacao = "ok"
    return {"classificacao": classificacao, "dias_sem_acao": dias}


def calcular_progresso_semanal(tarefas: list[dict], progresso: list[dict]) -> dict[str, Any]:
    total = len(tarefas)
    concluidas = sum(1 for item in tarefas if item.get("status") == "concluída")
    tempo_planejado = sum(int(item.get("tempo_estimado_minutos") or 0) for item in tarefas)
    tempo_realizado = sum(int(item.get("minutos_realizados") or 0) for item in progresso)
    frentes_com_acao = {item.get("frente_id") for item in progresso if item.get("frente_id")}
    percentual = round((concluidas / total) * 100, 1) if total else 0.0
    return {
        "total_tarefas": total,
        "tarefas_concluidas": concluidas,
        "percentual_concluido": percentual,
        "tempo_planejado": tempo_planejado,
        "tempo_realizado": tempo_realizado,
        "frentes_com_acao": len(frentes_com_acao),
    }


def calcular_variacao_saldo(saldo_atual: float | None, saldo_anterior: float | None) -> float | None:
    if saldo_atual is None or saldo_anterior is None:
        return None
    return round(float(saldo_atual) - float(saldo_anterior), 2)


def calcular_media_gasto_mensal(registros: list[dict], ano_mes: str) -> float:
    gastos = [
        float(item.get("gasto_semana") or 0)
        for item in registros
        if str(item.get("data_inicio", "")).startswith(ano_mes)
    ]
    return round(sum(gastos) / len(gastos), 2) if gastos else 0.0
