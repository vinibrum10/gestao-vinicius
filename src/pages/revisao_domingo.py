from __future__ import annotations

from datetime import date

import streamlit as st

from src.date_utils import formatar_data_br
from src.pages.common import dataframe, formatar_horas, opcoes_frentes
from src.services.financas_service import salvar_financas
from src.services.semanas_service import PESOS_SEMANA, criar_ou_atualizar_semana, inicio_semana
from src.services.tarefas_service import PRIORIDADES, criar_tarefa


def render() -> None:
    st.title("Planejar Semana")
    st.caption("Siga os passos abaixo para transformar sua semana em um plano simples.")
    frentes, mapa_frentes = opcoes_frentes()
    if not frentes:
        st.warning("Cadastre pelo menos uma área antes de criar a semana.")
        return

    st.subheader("1. Semana")
    with st.form("form_semana"):
        data_inicio = st.date_input("Início da semana", value=inicio_semana(), format="DD/MM/YYYY")
        st.caption(f"Semana começando em {formatar_data_br(data_inicio)}")
        st.subheader("2. Carga e tempo")
        peso = st.selectbox("Carga da semana", PESOS_SEMANA)
        tempo_estimado = st.number_input("Tempo livre total (horas)", min_value=0.0, step=0.5)
        tempo_util = st.number_input("Tempo real para foco (horas)", min_value=0.0, step=0.5)
        st.subheader("3. Foco")
        foco_nome = st.selectbox("Foco principal da semana", list(mapa_frentes.keys()))
        observacoes = st.text_area("Observações da semana")
        st.subheader("4. Dinheiro")
        gasto = st.number_input("Gasto da semana (R$)", min_value=0.0, step=10.0)
        saldo = st.number_input("Saldo atual (R$)", step=10.0)
        categoria = st.text_input("Categoria que mais pesou")
        inesperado = st.checkbox("Teve gasto inesperado?")
        obs_fin = st.text_area("Observações financeiras")
        salvar = st.form_submit_button("Salvar revisão e semana")

    if salvar:
        semana_id = criar_ou_atualizar_semana(
            data_inicio.isoformat(),
            mapa_frentes[foco_nome],
            tempo_estimado,
            tempo_util,
            peso,
            observacoes,
        )
        salvar_financas(semana_id, gasto, saldo, categoria, inesperado, obs_fin)
        st.success("Semana e finanças salvas.")
        st.session_state["semana_revisao_id"] = semana_id

    st.subheader("5. Ações principais")
    semana_id = st.session_state.get("semana_revisao_id")
    if not semana_id:
        st.info("Salve a semana acima para liberar o cadastro rápido de ações.")
        return
    with st.form("form_tarefas_revisao", clear_on_submit=True):
        titulo = st.text_input("Ação")
        frente = st.selectbox("Área", list(mapa_frentes.keys()), key="frente_tarefa_revisao")
        tempo = st.number_input("Tempo estimado (minutos)", min_value=0, value=60, step=15)
        data_planejada = st.date_input("Data planejada", value=date.today(), format="DD/MM/YYYY")
        st.caption(f"Data planejada selecionada: {formatar_data_br(data_planejada)}")
        prioridade = st.selectbox("Prioridade", PRIORIDADES)
        descricao = st.text_area("Observações")
        if st.form_submit_button("Adicionar ação"):
            criar_tarefa(semana_id, mapa_frentes[frente], titulo, descricao, tempo, data_planejada.isoformat(), prioridade)
            st.success("Ação criada.")

    st.subheader("6. Resumo")
    st.write(f"Plano salvo para uma semana de carga **{peso}**, com **{formatar_horas(tempo_util)}** reais para foco.")
    st.write(f"Foco principal: **{foco_nome}**.")
