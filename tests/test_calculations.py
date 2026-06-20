from datetime import date

from src.calculations import (
    calcular_divida_atencao,
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
