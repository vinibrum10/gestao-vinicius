from __future__ import annotations

import streamlit as st

from src.pages import agenda_manual, frentes


def render() -> None:
    st.title("Configurações")
    aba_areas, aba_tempo = st.tabs(["Áreas de Atenção", "Tempo da Semana"])
    with aba_areas:
        frentes.render(mostrar_titulo=False)
    with aba_tempo:
        agenda_manual.render(mostrar_titulo=False)
