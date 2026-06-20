import pandas as pd

from src.format_utils import formatar_moeda_br
from src.pages.common import formatar_dataframe_para_exibicao


def test_formatar_moeda_br():
    assert formatar_moeda_br(130) == "R$ 130,00"
    assert formatar_moeda_br(60.5) == "R$ 60,50"
    assert formatar_moeda_br(0) == "R$ 0,00"
    assert formatar_moeda_br(None) == "R$ 0,00"


def test_formatar_dataframe_para_exibicao_formata_datas_e_moeda():
    df = pd.DataFrame(
        [
            {
                "data_planejada": "2026-06-20",
                "gasto_semana": 130,
                "saldo_atual": 60.5,
            }
        ]
    )

    formatado = formatar_dataframe_para_exibicao(df)

    assert "data_planejada" not in formatado.columns
    assert "gasto_semana" not in formatado.columns
    assert "saldo_atual" not in formatado.columns
    assert formatado.loc[0, "Data planejada"] == "20/06/2026"
    assert formatado.loc[0, "Gasto da semana"] == "R$ 130,00"
    assert formatado.loc[0, "Saldo atual"] == "R$ 60,50"
