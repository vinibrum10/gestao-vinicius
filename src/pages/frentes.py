from __future__ import annotations

import streamlit as st

from src.pages.common import dataframe
from src.services.frentes_service import (
    NomeFrenteDuplicadoError,
    STATUS_FRENTES,
    atualizar_frente,
    criar_frente,
    listar_frentes,
    obter_frente,
)


def render(mostrar_titulo: bool = True) -> None:
    if mostrar_titulo:
        st.title("Áreas de Atenção")
    st.info("Áreas de Atenção são partes importantes da sua vida que o app ajuda você a não esquecer.")
    dataframe(listar_frentes(), "Nenhuma área cadastrada.")

    st.subheader("Criar nova área")
    with st.form("form_criar_frente", clear_on_submit=True):
        nome = st.text_input("Área")
        objetivo = st.text_area("Por que importa")
        status = st.selectbox("Situação", STATUS_FRENTES)
        importancia = st.slider("Importância", 1, 5, 3)
        minimo = st.number_input("Meta mínima da semana (minutos)", min_value=0, value=60, step=15)
        limite = st.number_input("Avisar se ficar sem avanço por X dias", min_value=1, value=14, step=1)
        if st.form_submit_button("Criar área") and nome:
            try:
                criar_frente(nome, objetivo, status, importancia, minimo, limite)
                st.success("Área criada.")
                st.rerun()
            except NomeFrenteDuplicadoError as exc:
                st.error("Já existe uma área com esse nome. Escolha outro nome.")

    st.subheader("Editar área")
    frentes = listar_frentes()
    if not frentes:
        return
    frente_id = st.selectbox(
        "Área para editar",
        [item["id"] for item in frentes],
        format_func=lambda item_id: next(item["nome"] for item in frentes if item["id"] == item_id),
    )
    atual = obter_frente(frente_id)
    if not atual:
        st.error("Área selecionada não encontrada.")
        return

    with st.form(f"form_editar_frente_{frente_id}"):
        nome = st.text_input("Área", value=atual["nome"], key=f"edit_nome_{frente_id}")
        objetivo = st.text_area("Por que importa", value=atual.get("objetivo") or "", key=f"edit_obj_{frente_id}")
        status = st.selectbox("Situação", STATUS_FRENTES, index=STATUS_FRENTES.index(atual["status"]), key=f"edit_status_{frente_id}")
        importancia = st.slider("Importância", 1, 5, int(atual["importancia"]), key=f"edit_imp_{frente_id}")
        minimo = st.number_input(
            "Meta mínima da semana (minutos)",
            min_value=0,
            value=int(atual["minimo_semanal_minutos"]),
            step=15,
            key=f"edit_minimo_{frente_id}",
        )
        limite = st.number_input(
            "Avisar se ficar sem avanço por X dias",
            min_value=1,
            value=int(atual["limite_alerta_dias"]),
            step=1,
            key=f"edit_limite_{frente_id}",
        )
        if st.form_submit_button("Salvar alterações"):
            try:
                atualizar_frente(atual["id"], nome, objetivo, status, importancia, minimo, limite)
                st.success("Área atualizada.")
                st.rerun()
            except NomeFrenteDuplicadoError as exc:
                st.error("Já existe uma área com esse nome. Escolha outro nome.")
