from __future__ import annotations

import streamlit as st

from src.database import init_db
from src.pages import configuracoes, financas, painel_semana, progresso, revisao_domingo, tarefas
from src.seed import seed_initial_data


def bootstrap() -> None:
    init_db()
    seed_initial_data()


def main() -> None:
    st.set_page_config(page_title="Gestão Vinicius", page_icon="GV", layout="wide")
    bootstrap()

    st.sidebar.title("Gestão Vinicius")
    pagina = st.sidebar.radio(
        "Navegação",
        [
            "Início",
            "Planejar Semana",
            "Minhas Ações",
            "Registrar Avanço",
            "Dinheiro",
            "Configurações",
        ],
    )

    paginas = {
        "Início": painel_semana.render,
        "Planejar Semana": revisao_domingo.render,
        "Minhas Ações": tarefas.render,
        "Registrar Avanço": progresso.render,
        "Dinheiro": financas.render,
        "Configurações": configuracoes.render,
    }
    paginas[pagina]()


if __name__ == "__main__":
    main()
