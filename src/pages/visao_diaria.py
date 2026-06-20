from __future__ import annotations

from datetime import date

import streamlit as st

from src.date_utils import formatar_data_br
from src.services.tarefas_service import atualizar_status_tarefa, listar_tarefas


def _bussola_energia(hoje: date) -> list[str]:
    mensagens = {
        0: ["Comece a semana escolhendo poucas ações essenciais."],
        1: ["Noite bloqueada: Aula Uniasselvi."],
        2: ["Home Office - Ler relatório Claude."],
        3: ["Noite bloqueada: Aula Uniasselvi."],
        4: ["Feche pendências pequenas antes do fim de semana."],
        5: ["Ritmo leve: mantenha só o mínimo importante."],
        6: ["Dia de revisão: observe energia, dinheiro e áreas esquecidas."],
    }
    return mensagens.get(hoje.weekday(), [])


def _acoes_de_hoje() -> list[dict]:
    hoje_iso = date.today().isoformat()
    return [acao for acao in listar_tarefas() if acao.get("data_planejada") == hoje_iso]


def render() -> None:
    hoje = date.today()
    st.title("Visão Diária")
    st.caption(f"Hoje é {formatar_data_br(hoje)}")

    st.subheader("Hábitos de Manutenção")
    col1, col2 = st.columns(2)
    col1.checkbox("Leitura no Metrô", key=f"habito_leitura_{hoje.isoformat()}")
    col2.checkbox("Duolingo", key=f"habito_duolingo_{hoje.isoformat()}")

    st.subheader("Ações de Hoje")
    acoes = _acoes_de_hoje()
    if not acoes:
        st.info("Nenhuma ação planejada para hoje.")
    for acao in acoes:
        concluida = acao["status"] == "concluída"
        with st.container(border=True):
            st.markdown(f"**{acao['titulo']}**")
            st.caption(f"Área: {acao['frente']} | Prioridade: {acao['prioridade']} | Status: {acao['status']}")
            if acao.get("descricao"):
                st.write(acao["descricao"])
            if st.checkbox("Concluir agora", value=concluida, key=f"acao_hoje_{acao['id']}", disabled=concluida):
                atualizar_status_tarefa(acao["id"], "concluída", acao["frente_id"])
                st.success("Ação concluída.")
                st.rerun()

    st.subheader("Bússola de Energia")
    for mensagem in _bussola_energia(hoje):
        st.write(f"- {mensagem}")
