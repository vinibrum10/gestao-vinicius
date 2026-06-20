from __future__ import annotations

import streamlit as st

from src.format_utils import formatar_moeda_br
from src.pages.common import dataframe
from src.services.financas_service import listar_despesas_recentes, obter_resumo_orcamento, registrar_despesa


def render() -> None:
    st.title("Meu Orçamento")

    resumo = obter_resumo_orcamento()
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Atual", formatar_moeda_br(resumo["saldo_atual"]))
    col2.metric("Gasto da Semana", formatar_moeda_br(resumo["gasto_semana"]))
    col3.metric("Margem Livre", formatar_moeda_br(resumo["margem_livre"]))

    st.subheader("Registrar Despesa")
    with st.form("registrar_despesa", clear_on_submit=True):
        valor_col, categoria_col, botao_col = st.columns([2, 4, 1])
        valor = valor_col.number_input("Valor (R$)", min_value=0.0, step=5.0)
        categoria = categoria_col.text_input("Categoria")
        salvar = botao_col.form_submit_button("Salvar")
        if salvar and valor > 0:
            registrar_despesa(valor, categoria)
            st.success("Despesa registrada.")
            st.rerun()

    st.subheader("Despesas recentes")
    despesas = listar_despesas_recentes()
    dataframe(despesas, "Nenhuma despesa registrada.")
