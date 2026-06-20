from __future__ import annotations

from datetime import date, datetime, time
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


def _parse_datetime(value: str | datetime | date | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if isinstance(parsed, datetime):
        return parsed
    return None


def _normalizar_intervalo(item: dict) -> tuple[datetime, datetime] | None:
    inicio = _parse_datetime(item.get("inicio") or item.get("start") or item.get("data_inicio"))
    fim = _parse_datetime(item.get("fim") or item.get("end") or item.get("data_fim"))
    if not inicio or not fim or fim <= inicio:
        return None
    if inicio.tzinfo and fim.tzinfo:
        fim = fim.astimezone(inicio.tzinfo)
    elif inicio.tzinfo and not fim.tzinfo:
        fim = fim.replace(tzinfo=inicio.tzinfo)
    elif fim.tzinfo and not inicio.tzinfo:
        inicio = inicio.replace(tzinfo=fim.tzinfo)
    return inicio, fim


def _horas_ocupadas_por_intervalos(intervalos: list[tuple[datetime, datetime]]) -> float:
    if not intervalos:
        return 0.0
    ordenados = sorted(intervalos, key=lambda item: item[0])
    mesclados = [ordenados[0]]
    for inicio, fim in ordenados[1:]:
        ultimo_inicio, ultimo_fim = mesclados[-1]
        if inicio <= ultimo_fim:
            mesclados[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            mesclados.append((inicio, fim))
    segundos = sum((fim - inicio).total_seconds() for inicio, fim in mesclados)
    return segundos / 3600


def calcular_disponibilidade_real(eventos_google: list[dict], horas_fixas_semana: float | int | list[dict] | None) -> float:
    intervalos = []
    for evento in eventos_google or []:
        intervalo = _normalizar_intervalo(evento)
        if intervalo:
            intervalos.append(intervalo)

    horas_fixas = 0.0
    if isinstance(horas_fixas_semana, list):
        for bloco in horas_fixas_semana:
            intervalo = _normalizar_intervalo(bloco)
            if intervalo:
                intervalos.append(intervalo)
            else:
                horas_fixas += float(bloco.get("horas", 0) or 0)
    elif horas_fixas_semana is not None:
        horas_fixas = float(horas_fixas_semana or 0)

    horas_ocupadas = _horas_ocupadas_por_intervalos(intervalos) + horas_fixas
    return round(max(0.0, 168.0 - horas_ocupadas), 1)
