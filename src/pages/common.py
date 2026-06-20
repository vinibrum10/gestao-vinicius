from __future__ import annotations

import pandas as pd
import streamlit as st

from src.date_utils import formatar_data_br, formatar_intervalo_br
from src.format_utils import formatar_moeda_br
from src.services.frentes_service import listar_frentes
from src.services.semanas_service import inicio_semana, listar_semanas

COLUNAS_MOEDA = {"gasto_semana", "saldo_atual", "variacao_saldo"}
COLUNAS_TECNICAS = {
    "id",
    "semana_id",
    "frente_id",
    "foco_principal_frente_id",
    "criada_em",
    "atualizada_em",
    "concluida_em",
}
NOMES_AMIGAVEIS = {
    "nome": "Área",
    "objetivo": "Por que importa",
    "status": "Situação",
    "importancia": "Importância",
    "minimo_semanal_minutos": "Meta mínima da semana",
    "limite_alerta_dias": "Avisar sem avanço por X dias",
    "ultima_acao_data": "Última ação",
    "classificacao": "Atenção",
    "dias_sem_acao": "Dias sem avanço",
    "titulo": "Ação",
    "descricao": "Observações",
    "tempo_estimado_minutos": "Tempo estimado",
    "data_planejada": "Data planejada",
    "prioridade": "Prioridade",
    "frente": "Área",
    "data_inicio": "Início",
    "data_fim": "Fim",
    "peso_semana": "Carga da semana",
    "tempo_livre_estimado_horas": "Tempo livre total",
    "tempo_livre_util_horas": "Tempo real para foco",
    "foco_principal": "Foco principal",
    "gasto_semana": "Gasto da semana",
    "saldo_atual": "Saldo atual",
    "categoria_mais_pesada": "Categoria que mais pesou",
    "teve_gasto_inesperado": "Gasto inesperado",
    "observacoes": "Observações",
    "variacao_saldo": "Variação do saldo",
    "minutos_realizados": "Minutos realizados",
    "resumo_acao": "O que foi feito",
    "data_acao": "Data",
    "tarefas_concluidas": "Ações concluídas",
    "tipo": "Tipo de compromisso",
    "hora_inicio": "Hora início",
    "hora_fim": "Hora fim",
    "nivel_energia": "Energia",
}


def dataframe(registros: list[dict], vazio: str = "Nenhum registro encontrado.") -> None:
    if registros:
        st.dataframe(formatar_dataframe_para_exibicao(pd.DataFrame(registros)), use_container_width=True, hide_index=True)
    else:
        st.info(vazio)


def formatar_dataframe_para_exibicao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop(columns=[coluna for coluna in COLUNAS_TECNICAS if coluna in df.columns])
    for coluna in df.columns:
        if coluna.endswith("_data") or coluna in {"data", "data_inicio", "data_fim", "data_planejada", "ultima_acao_data", "concluida_em"}:
            df[coluna] = df[coluna].apply(formatar_data_br)
        if coluna in COLUNAS_MOEDA:
            df[coluna] = df[coluna].apply(formatar_moeda_br)
        if coluna == "teve_gasto_inesperado":
            df[coluna] = df[coluna].apply(lambda valor: "Sim" if valor else "Não")
        if coluna in {"tempo_estimado_minutos", "minimo_semanal_minutos"}:
            df[coluna] = df[coluna].apply(lambda valor: f"{int(valor)} min" if pd.notna(valor) else "")
    df = df.rename(columns={chave: valor for chave, valor in NOMES_AMIGAVEIS.items() if chave in df.columns})
    return df


def formatar_horas(valor: float | int | None) -> str:
    if valor is None:
        return "0h"
    numero = float(valor)
    if numero.is_integer():
        return f"{int(numero)}h"
    return f"{numero:.1f}".replace(".", ",") + "h"


def opcoes_frentes() -> tuple[list[dict], dict[str, int]]:
    frentes = listar_frentes()
    mapa = {item["nome"]: item["id"] for item in frentes}
    return frentes, mapa


def opcoes_semanas() -> tuple[list[dict], dict[str, int]]:
    semanas = _priorizar_semana_atual(listar_semanas())
    mapa = {formatar_intervalo_br(item["data_inicio"], item["data_fim"]): item["id"] for item in semanas}
    return semanas, mapa


def _priorizar_semana_atual(semanas: list[dict]) -> list[dict]:
    atual = inicio_semana().isoformat()
    return sorted(semanas, key=lambda item: (item.get("data_inicio") != atual, item.get("data_inicio", "")), reverse=False)
