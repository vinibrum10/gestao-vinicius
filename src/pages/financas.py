from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.date_utils import formatar_data_br
from src.format_utils import formatar_moeda_br
from src.pages.common import dataframe, opcoes_semanas
from src.services.financas_service import listar_historico_financeiro, salvar_financas


def render() -> None:
    st.title("Dinheiro")
    semanas, mapa = opcoes_semanas()
    if not semanas:
        st.warning("Crie uma semana antes de registrar dinheiro.")
        return

    with st.form("form_financas"):
        semana = st.selectbox("Semana", list(mapa.keys()))
        gasto = st.number_input("Gasto semanal (R$)", min_value=0.0, step=10.0)
        saldo = st.number_input("Saldo atual (R$)", step=10.0)
        categoria = st.text_input("Categoria mais pesada")
        inesperado = st.checkbox("Teve gasto inesperado?")
        observacoes = st.text_area("Observações")
        if st.form_submit_button("Salvar finanças"):
            salvar_financas(mapa[semana], gasto, saldo, categoria, inesperado, observacoes)
            st.success("Dinheiro salvo.")
            st.rerun()

    historico = listar_historico_financeiro()
    st.subheader("Histórico financeiro")
    dataframe(historico, "Nenhum registro financeiro.")
    if historico:
        df = pd.DataFrame(historico)
        df["semana"] = df["data_inicio"].apply(formatar_data_br)
        df_grafico = df.melt(
            id_vars=["semana"],
            value_vars=["gasto_semana", "saldo_atual"],
            var_name="indicador",
            value_name="valor",
        )
        df_grafico["valor_formatado"] = df_grafico["valor"].apply(formatar_moeda_br)
        fig = px.line(
            df_grafico,
            x="semana",
            y="valor",
            color="indicador",
            labels={"semana": "Semana", "valor": "Valor (R$)", "indicador": "Indicador"},
            custom_data=["valor_formatado"],
        )
        fig.update_traces(hovertemplate="%{x}<br>%{legendgroup}: %{customdata[0]}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)
