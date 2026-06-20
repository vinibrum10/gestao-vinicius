from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from src.date_utils import formatar_data_br
from src.pages.common import dataframe, opcoes_frentes, opcoes_semanas
from src.services.frentes_service import listar_frentes
from src.services.progresso_service import listar_progresso, registrar_progresso, tarefas_concluidas_por_semana, tempo_por_frente


def render() -> None:
    st.title("Registrar Avanço")
    st.info("Use esta tela para registrar o que você realmente fez, mesmo que tenha sido pouco.")
    semanas, mapa_semanas = opcoes_semanas()
    frentes, mapa_frentes = opcoes_frentes()
    if semanas:
        with st.form("form_progresso", clear_on_submit=True):
            semana = st.selectbox("Semana", list(mapa_semanas.keys()))
            frente = st.selectbox("Área", list(mapa_frentes.keys()))
            minutos = st.number_input("Minutos realizados", min_value=0, value=30, step=15)
            data_acao = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            resumo = st.text_area("O que foi feito")
            if st.form_submit_button("Registrar avanço") and resumo:
                registrar_progresso(mapa_semanas[semana], mapa_frentes[frente], minutos, resumo, data_acao.isoformat())
                st.success("Avanço registrado.")
                st.rerun()

    st.subheader("Ações concluídas por semana")
    concluidas = tarefas_concluidas_por_semana()
    dataframe(concluidas, "Nenhuma semana cadastrada.")
    if concluidas:
        df_concluidas = pd.DataFrame(concluidas)
        df_concluidas["semana"] = df_concluidas["data_inicio"].apply(formatar_data_br)
        st.plotly_chart(px.bar(df_concluidas, x="semana", y="tarefas_concluidas", labels={"semana": "Semana", "tarefas_concluidas": "Ações concluídas"}), use_container_width=True)

    st.subheader("Tempo realizado por área")
    tempos = tempo_por_frente()
    dataframe(tempos, "Nenhum progresso registrado.")
    if tempos:
        st.plotly_chart(px.bar(pd.DataFrame(tempos), x="frente", y="minutos_realizados", labels={"frente": "Área", "minutos_realizados": "Minutos realizados"}), use_container_width=True)

    st.subheader("Áreas esquecidas")
    dataframe([f for f in listar_frentes() if f["classificacao"] in ("atenção", "crítico")], "Nenhuma área esquecida.")

    st.subheader("Resumo mensal simples")
    progresso = listar_progresso()
    if progresso:
        df = pd.DataFrame(progresso)
        df["mes"] = df["data_acao"].str.slice(0, 7)
        resumo = df.groupby("mes", as_index=False)["minutos_realizados"].sum()
        st.dataframe(resumo, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum avanço registrado.")
