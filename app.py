from __future__ import annotations

import streamlit as st

from src.database import init_db
from src.pages import configuracoes, demandas, financas, revisao_domingo
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
            "📍 Minhas Demandas",
            "💰 Meu Orçamento",
            "🧭 Planejamento de Domingo",
            "⚙️ Configurações",
        ],
    )

    paginas = {
        "📍 Minhas Demandas": demandas.render,
        "💰 Meu Orçamento": financas.render,
        "🧭 Planejamento de Domingo": revisao_domingo.render,
        "⚙️ Configurações": configuracoes.render,
    }
    paginas[pagina]()


if __name__ == "__main__":
    main()
