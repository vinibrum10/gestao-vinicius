from datetime import date

from src.date_utils import formatar_data_br, formatar_intervalo_br
from src.services.semanas_service import fim_semana, inicio_semana


def test_semana_atual_em_2026_06_20_comeca_na_segunda_e_termina_no_domingo():
    inicio = inicio_semana(date(2026, 6, 20))
    fim = fim_semana(inicio)
    assert inicio == date(2026, 6, 15)
    assert fim == date(2026, 6, 21)


def test_segunda_retorna_a_propria_data_como_inicio():
    inicio = inicio_semana(date(2026, 6, 15))
    assert inicio == date(2026, 6, 15)
    assert fim_semana(inicio) == date(2026, 6, 21)


def test_domingo_retorna_segunda_anterior_e_proprio_domingo_como_fim():
    inicio = inicio_semana(date(2026, 6, 21))
    assert inicio == date(2026, 6, 15)
    assert fim_semana(inicio) == date(2026, 6, 21)


def test_calculo_nao_pula_para_semana_futura():
    assert inicio_semana(date(2026, 6, 20)) < date(2026, 6, 20)
    assert fim_semana(inicio_semana(date(2026, 6, 20))) > date(2026, 6, 20)


def test_formatar_data_br():
    assert formatar_data_br("2026-06-20") == "20/06/2026"
    assert formatar_data_br("2026/06/20") == "20/06/2026"
    assert formatar_data_br(date(2026, 6, 20)) == "20/06/2026"
    assert formatar_data_br("") == ""
    assert formatar_data_br(None) == ""
    assert formatar_data_br("data invalida") == "data invalida"


def test_formatar_intervalo_br():
    assert formatar_intervalo_br("2026-06-15", "2026-06-21") == "15/06/2026 a 21/06/2026"
    assert formatar_intervalo_br("", None) == ""
