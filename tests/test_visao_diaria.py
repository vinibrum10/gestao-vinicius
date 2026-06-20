from datetime import date

from src.pages.visao_diaria import _bussola_energia


def test_bussola_de_energia_quarta_feira():
    mensagens = _bussola_energia(date(2026, 6, 17))
    assert "Home Office - Ler relatório Claude." in mensagens


def test_bussola_de_energia_terca_e_quinta():
    assert "Noite bloqueada: Aula Uniasselvi." in _bussola_energia(date(2026, 6, 16))
    assert "Noite bloqueada: Aula Uniasselvi." in _bussola_energia(date(2026, 6, 18))
