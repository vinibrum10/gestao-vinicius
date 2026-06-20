from __future__ import annotations

from collections import defaultdict

import streamlit as st

from src.services.semanas_service import obter_semana_atual
from src.services.tarefas_service import atualizar_status_tarefa, listar_tarefas


def render() -> None:
    st.title("Minhas Demandas")

    with st.expander("Adicionar Demanda Rápida", expanded=False):
        st.info("Use Planejamento de Domingo para cadastrar novas demandas com área, semana e prioridade.")

    semana = obter_semana_atual()
    if not semana:
        st.warning("Crie a semana atual em Planejamento de Domingo para ver suas demandas.")
        return

    tarefas = [
        tarefa
        for tarefa in listar_tarefas(semana_id=semana["id"])
        if tarefa["status"] != "concluída"
    ]
    if not tarefas:
        st.success("Nenhuma demanda pendente nesta semana.")
        return

    por_area = defaultdict(list)
    for tarefa in tarefas:
        por_area[tarefa["frente"]].append(tarefa)

    for area, demandas in sorted(por_area.items()):
        with st.expander(f"{area} ({len(demandas)})", expanded=True):
            for demanda in demandas:
                col_titulo, col_prioridade, col_concluir = st.columns([5, 2, 1])
                col_titulo.write(f"**{demanda['titulo']}**")
                col_prioridade.caption(f"Prioridade: {demanda['prioridade']}")
                if col_concluir.button("Concluir", key=f"concluir_demanda_{demanda['id']}"):
                    atualizar_status_tarefa(demanda["id"], "concluída", demanda["frente_id"])
                    st.rerun()
