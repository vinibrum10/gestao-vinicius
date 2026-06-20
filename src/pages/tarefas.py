from __future__ import annotations

from datetime import date

import streamlit as st

from src.pages.common import dataframe, opcoes_frentes, opcoes_semanas
from src.services.tarefas_service import PRIORIDADES, STATUS_TAREFAS, atualizar_status_tarefa, criar_tarefa, listar_tarefas


def render() -> None:
    st.title("Minhas Ações")
    semanas, mapa_semanas = opcoes_semanas()
    frentes, mapa_frentes = opcoes_frentes()
    if not semanas:
        st.warning("Crie uma semana em Planejar Semana antes de cadastrar ações.")
        return

    with st.form("form_criar_tarefa", clear_on_submit=True):
        semana = st.selectbox("Semana", list(mapa_semanas.keys()))
        frente = st.selectbox("Área", list(mapa_frentes.keys()))
        titulo = st.text_input("Ação")
        descricao = st.text_area("Observações")
        tempo = st.number_input("Tempo estimado (minutos)", min_value=0, value=60, step=15)
        data_planejada = st.date_input("Data planejada", value=date.today(), format="DD/MM/YYYY")
        prioridade = st.selectbox("Prioridade", PRIORIDADES)
        if st.form_submit_button("Criar ação") and titulo:
            criar_tarefa(mapa_semanas[semana], mapa_frentes[frente], titulo, descricao, tempo, data_planejada.isoformat(), prioridade)
            st.success("Ação criada.")
            st.rerun()

    st.subheader("Filtros")
    c1, c2, c3 = st.columns(3)
    semana_f = c1.selectbox("Semana", ["todas"] + list(mapa_semanas.keys()), key="filtro_semana")
    frente_f = c2.selectbox("Área", ["todas"] + list(mapa_frentes.keys()), key="filtro_frente")
    status_f = c3.selectbox("Status", ["todos"] + STATUS_TAREFAS, key="filtro_status")
    semana_id = None if semana_f == "todas" else mapa_semanas[semana_f]
    frente_id = None if frente_f == "todas" else mapa_frentes[frente_f]
    tarefas = listar_tarefas(semana_id, frente_id, status_f)
    dataframe(tarefas, "Nenhuma ação encontrada.")

    st.subheader("Alterar status")
    if tarefas:
        opcoes = {f"{t['titulo']} ({t['frente']})": t for t in tarefas}
        escolha = st.selectbox("Ação", list(opcoes.keys()))
        novo_status = st.selectbox("Novo status", STATUS_TAREFAS)
        if st.button("Atualizar status"):
            tarefa = opcoes[escolha]
            atualizar_status_tarefa(tarefa["id"], novo_status, tarefa["frente_id"])
            st.success("Status atualizado.")
            st.rerun()
