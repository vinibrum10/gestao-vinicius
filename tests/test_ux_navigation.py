from pathlib import Path

from src.pages.common import formatar_dataframe_para_exibicao


def test_menu_principal_usa_nova_navegacao():
    conteudo = Path("app.py").read_text(encoding="utf-8")

    for nome in ["📍 Minhas Demandas", "💰 Meu Orçamento", "🧭 Planejamento de Domingo", "⚙️ Configurações"]:
        assert f'"{nome}"' in conteudo

    for nome_antigo in ["Visão Diária", "Resumo da Semana", "Minhas Ações", "Registrar Avanço", "Dinheiro", "Início", "Painel da Semana"]:
        assert f'"{nome_antigo}"' not in conteudo

    assert conteudo.index('"📍 Minhas Demandas"') < conteudo.index('"💰 Meu Orçamento"')


def test_dataframe_de_exibicao_nao_mostra_campos_tecnicos():
    import pandas as pd

    formatado = formatar_dataframe_para_exibicao(
        pd.DataFrame(
            [
                {
                    "id": 1,
                    "semana_id": 2,
                    "frente_id": 3,
                    "titulo": "Ação teste",
                    "frente": "Doutorado",
                    "data_planejada": "2026-06-20",
                }
            ]
        )
    )

    assert "id" not in formatado.columns
    assert "semana_id" not in formatado.columns
    assert "frente_id" not in formatado.columns
    assert list(formatado.columns) == ["Ação", "Área", "Data planejada"]
