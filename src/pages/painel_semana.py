from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.calculations import calcular_progresso_semanal
from src.date_utils import formatar_intervalo_br
from src.format_utils import formatar_moeda_br
from src.pages.common import dataframe, formatar_horas
from src.services.financas_service import obter_financas_semana
from src.services.frentes_service import listar_frentes, obter_frente
from src.services.progresso_service import listar_progresso
from src.services.semanas_service import obter_semana_atual
from src.services.tarefas_service import listar_tarefas


def _frase_orientativa(semana: dict, esquecidas: list[dict], financas: dict | None) -> str:
    if semana["peso_semana"] == "muito pesada":
        return "Sua semana está muito pesada. Escolha poucas ações e mantenha o mínimo nas áreas importantes."
    if esquecidas:
        return f"{esquecidas[0]['nome']} está sem avanço. Reserve ao menos uma ação curta."
    if not financas:
        return "Você ainda não revisou seu dinheiro nesta semana."
    return "Sua semana já tem uma base. Agora mantenha as ações pequenas e visíveis."


def render() -> None:
    st.title("Início")
    semana = obter_semana_atual()
    if not semana:
        st.warning("A semana atual ainda não foi criada. Vá em Planejar Semana para começar.")
        return

    tarefas = listar_tarefas(semana_id=semana["id"])
    progresso = listar_progresso(semana_id=semana["id"])
    resumo = calcular_progresso_semanal(tarefas, progresso)
    financas = obter_financas_semana(semana["id"])
    esquecidas = [area for area in listar_frentes() if area["classificacao"] in ("atenção", "crítico")]
    foco = obter_frente(semana["foco_principal_frente_id"]) if semana.get("foco_principal_frente_id") else None

    st.info(_frase_orientativa(semana, esquecidas, financas))
    st.subheader(f"Semana de {formatar_intervalo_br(semana['data_inicio'], semana['data_fim'])}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Carga da semana", semana["peso_semana"])
    col2.metric("Tempo real para foco", formatar_horas(semana["tempo_livre_util_horas"]))
    col3.metric("Foco principal", foco["nome"] if foco else "-")
    col4.metric("Conclusão", f"{resumo['percentual_concluido']}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Tempo livre total", formatar_horas(semana["tempo_livre_estimado_horas"]))
    col6.metric("Ações pendentes", len([acao for acao in tarefas if acao["status"] != "concluída"]))
    col7.metric("Ações concluídas", resumo["tarefas_concluidas"])

    st.subheader("Ações da semana")
    pendentes = [t for t in tarefas if t["status"] != "concluída"]
    concluidas = [t for t in tarefas if t["status"] == "concluída"]
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Pendentes")
        dataframe(pendentes, "Nenhuma ação pendente.")
    with c2:
        st.caption("Concluídas")
        dataframe(concluidas, "Nenhuma ação concluída.")

    st.subheader("Áreas esquecidas")
    dataframe(esquecidas, "Nenhuma área esquecida agora.")

    st.subheader("Resumo do dinheiro")
    if financas:
        f1, f2, f3 = st.columns(3)
        f1.metric("Gasto da semana", formatar_moeda_br(financas["gasto_semana"]))
        f2.metric("Saldo atual", formatar_moeda_br(financas["saldo_atual"]))
        f3.metric("Categoria mais pesada", financas["categoria_mais_pesada"] or "-")
    else:
        st.info("Você ainda não revisou seu dinheiro nesta semana.")

    st.subheader("Últimos avanços")
    if progresso:
        dataframe(progresso[:5], "Nenhum avanço registrado nesta semana.")
        df = pd.DataFrame(progresso)
        agrupado = df.groupby("frente", as_index=False)["minutos_realizados"].sum()
        fig = px.bar(agrupado, x="frente", y="minutos_realizados", labels={"frente": "Área", "minutos_realizados": "Minutos realizados"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum avanço registrado nesta semana.")
