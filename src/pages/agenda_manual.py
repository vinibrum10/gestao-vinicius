from __future__ import annotations

from datetime import date

import streamlit as st

from src.pages.common import dataframe, opcoes_semanas
from src.services.agenda_service import NIVEIS_ENERGIA, TIPOS_BLOCO, criar_bloco, listar_blocos


def render(mostrar_titulo: bool = True) -> None:
    if mostrar_titulo:
        st.title("Tempo da Semana")
    st.info("Use esta área para registrar os principais blocos da sua semana.")
    semanas, mapa = opcoes_semanas()
    if not semanas:
        st.warning("Crie uma semana antes de cadastrar blocos de tempo.")
        return

    with st.form("form_bloco", clear_on_submit=True):
        semana = st.selectbox("Semana", list(mapa.keys()))
        data_bloco = st.date_input("Data", value=date.today())
        c1, c2 = st.columns(2)
        hora_inicio = c1.time_input("Hora início")
        hora_fim = c2.time_input("Hora fim")
        tipo = st.selectbox("Tipo de compromisso", TIPOS_BLOCO)
        titulo = st.text_input("Título")
        energia = st.selectbox("Energia", NIVEIS_ENERGIA)
        observacoes = st.text_area("Observações")
        if st.form_submit_button("Cadastrar bloco") and titulo:
            criar_bloco(mapa[semana], data_bloco.isoformat(), hora_inicio.strftime("%H:%M"), hora_fim.strftime("%H:%M"), tipo, titulo, energia, observacoes)
            st.success("Bloco cadastrado.")
            st.rerun()

    semana_filtro = st.selectbox("Visualizar semana", ["todas"] + list(mapa.keys()))
    semana_id = None if semana_filtro == "todas" else mapa[semana_filtro]
    dataframe(listar_blocos(semana_id), "Nenhum bloco cadastrado.")
