from datetime import date

from src.calculations import (
    calcular_divida_atencao,
    calcular_disponibilidade_real,
    calcular_media_gasto_mensal,
    calcular_progresso_semanal,
    calcular_variacao_saldo,
)


def test_divida_atencao_classifica_ok_atencao_critico_e_pausada():
    hoje = date(2026, 6, 20)
    assert calcular_divida_atencao("2026-06-18", 5, "ativa", hoje)["classificacao"] == "ok"
    assert calcular_divida_atencao("2026-06-10", 5, "ativa", hoje)["classificacao"] == "atenção"
    assert calcular_divida_atencao("2026-06-01", 5, "ativa", hoje)["classificacao"] == "crítico"
    assert calcular_divida_atencao("2026-06-01", 5, "pausada", hoje)["classificacao"] == "pausada"


def test_progresso_semanal_resume_tarefas_e_tempo():
    tarefas = [
        {"status": "concluída", "tempo_estimado_minutos": 60},
        {"status": "pendente", "tempo_estimado_minutos": 30},
    ]
    progresso = [{"frente_id": 1, "minutos_realizados": 45}, {"frente_id": 2, "minutos_realizados": 15}]
    resultado = calcular_progresso_semanal(tarefas, progresso)
    assert resultado["total_tarefas"] == 2
    assert resultado["tarefas_concluidas"] == 1
    assert resultado["percentual_concluido"] == 50.0
    assert resultado["tempo_planejado"] == 90
    assert resultado["tempo_realizado"] == 60
    assert resultado["frentes_com_acao"] == 2


def test_financas():
    assert calcular_variacao_saldo(1200, 1000) == 200
    registros = [{"data_inicio": "2026-06-01", "gasto_semana": 100}, {"data_inicio": "2026-06-08", "gasto_semana": 200}]
    assert calcular_media_gasto_mensal(registros, "2026-06") == 150


def test_disponibilidade_real_deduz_eventos_e_horas_fixas():
    eventos = [
        {"inicio": "2026-06-15T09:00:00-03:00", "fim": "2026-06-15T11:00:00-03:00"},
        {"inicio": "2026-06-16T14:00:00-03:00", "fim": "2026-06-16T15:30:00-03:00"},
    ]
    assert calcular_disponibilidade_real(eventos, 40) == 124.5


def test_disponibilidade_real_mescla_eventos_sobrepostos():
    eventos = [
        {"inicio": "2026-06-15T09:00:00-03:00", "fim": "2026-06-15T11:00:00-03:00"},
        {"inicio": "2026-06-15T10:00:00-03:00", "fim": "2026-06-15T12:00:00-03:00"},
    ]
    assert calcular_disponibilidade_real(eventos, 0) == 165


def test_disponibilidade_real_nao_retorna_negativo():
    eventos = [{"inicio": "2026-06-15", "fim": "2026-06-22"}]
    assert calcular_disponibilidade_real(eventos, 20) == 0
