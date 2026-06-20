from __future__ import annotations

import streamlit as st

from src.format_utils import formatar_moeda_br
from src.pages.common import dataframe
from src.services.financas_service import atualizar_caixa_semana, listar_despesas_recentes, obter_resumo_orcamento
from src.services.semanas_service import obter_semana_atual


def render() -> None:
    st.title("Meu Orçamento")

    resumo = obter_resumo_orcamento()
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Atual", formatar_moeda_br(resumo["saldo_atual"]))
    col2.metric("Gasto Acumulado", formatar_moeda_br(resumo["gasto_semana"]))
    col3.metric("Margem", formatar_moeda_br(resumo["margem_livre"]))

    semana = obter_semana_atual()
    if not semana:
        st.warning("Crie a semana atual em Planejamento de Domingo para atualizar o caixa.")
        return

    st.subheader("Atualização de Caixa")
    with st.form("atualizacao_caixa", clear_on_submit=False):
        saldo_col, gasto_col, botao_col = st.columns([2, 2, 1])
        novo_saldo = saldo_col.number_input("Novo Saldo", min_value=0.0, value=float(resumo["saldo_atual"]), step=50.0)
        novo_gasto = gasto_col.number_input("Somar Gasto", min_value=0.0, step=5.0)
        salvar = botao_col.form_submit_button("Salvar")
        if salvar:
            atualizar_caixa_semana(semana["id"], novo_saldo, novo_gasto)
            st.success("Caixa atualizado.")
            st.rerun()

    with st.expander("Histórico", expanded=False):
        despesas = listar_despesas_recentes()
        dataframe(despesas, "Nenhuma despesa registrada.")
