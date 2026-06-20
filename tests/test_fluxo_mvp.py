from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import database
from src.pages.common import formatar_dataframe_para_exibicao, opcoes_semanas
from src.seed import seed_initial_data
from src.services.agenda_service import criar_bloco, listar_blocos
from src.services.financas_service import (
    listar_despesas_recentes,
    listar_historico_financeiro,
    obter_financas_semana,
    obter_resumo_orcamento,
    registrar_despesa,
    salvar_financas,
)
from src.services.frentes_service import NomeFrenteDuplicadoError, atualizar_frente, listar_frentes, obter_frente
from src.services.progresso_service import listar_progresso, registrar_progresso
from src.services.semanas_service import criar_ou_atualizar_semana, obter_semana_atual
from src.services.tarefas_service import atualizar_status_tarefa, criar_tarefa, listar_tarefas


@pytest.fixture()
def banco_temporario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "gestao_vinicius_teste.db")
    database.init_db()
    seed_initial_data()
    return database.DB_PATH


def test_persistencia_semana_atual_e_tarefa_no_sqlite(banco_temporario):
    frentes = listar_frentes()
    frente_id = frentes[0]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 8, 6, "moderada", "teste")
    tarefa_id = criar_tarefa(semana_id, frente_id, "Tarefa de teste", "", 45, "2026-06-20", "alta")

    assert banco_temporario.exists()
    semana = obter_semana_atual()
    tarefas = listar_tarefas(semana_id=semana_id)

    assert semana["data_inicio"] == "2026-06-15"
    assert semana["data_fim"] == "2026-06-21"
    assert tarefas[0]["id"] == tarefa_id
    assert tarefas[0]["titulo"] == "Tarefa de teste"


def test_filtros_de_tarefas_encontram_semana_atual_frente_e_status(banco_temporario):
    frentes = listar_frentes()
    frente_id = frentes[0]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 8, 6, "moderada", "teste")
    criar_tarefa(semana_id, frente_id, "Tarefa filtravel", "", 45, "2026-06-20", "alta")

    por_semana = listar_tarefas(semana_id=semana_id)
    por_frente = listar_tarefas(frente_id=frente_id)
    por_status = listar_tarefas(status="pendente")

    assert [t["titulo"] for t in por_semana] == ["Tarefa filtravel"]
    assert [t["titulo"] for t in por_frente] == ["Tarefa filtravel"]
    assert [t["titulo"] for t in por_status] == ["Tarefa filtravel"]


def test_opcoes_de_semana_priorizam_semana_atual_mesmo_com_semana_futura(banco_temporario):
    frentes = listar_frentes()
    frente_id = frentes[0]["id"]
    criar_ou_atualizar_semana("2026-06-15", frente_id, 8, 6, "moderada", "atual")
    criar_ou_atualizar_semana("2026-06-29", frente_id, 8, 6, "pesada", "futura")

    _, mapa = opcoes_semanas()
    opcoes = list(mapa.keys())

    assert opcoes[0] == "15/06/2026 a 21/06/2026"
    assert "29/06/2026 a 05/07/2026" in opcoes


def test_tarefa_criada_na_revisao_aparece_em_tarefas_e_no_painel_com_data_br(banco_temporario):
    frentes = listar_frentes()
    frente_id = frentes[0]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 8, 6, "moderada", "semana")
    criar_tarefa(semana_id, frente_id, "Tarefa da revisão", "", 30, "2026-06-20", "média")

    tarefas_tela = listar_tarefas(semana_id=semana_id)
    tarefas_painel = listar_tarefas(semana_id=obter_semana_atual()["id"])
    tarefas_formatadas = formatar_dataframe_para_exibicao(pd.DataFrame(tarefas_tela))

    assert tarefas_tela[0]["titulo"] == "Tarefa da revisão"
    assert tarefas_painel[0]["titulo"] == "Tarefa da revisão"
    assert tarefas_formatadas.loc[0, "Data planejada"] == "20/06/2026"


def test_financas_permanecem_numericas_no_banco_e_formatadas_na_exibicao(banco_temporario):
    frentes = listar_frentes()
    frente_id = frentes[0]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 8, 6, "moderada", "semana")

    salvar_financas(semana_id, 130, 60.5, "Mercado", False, "")

    registro = obter_financas_semana(semana_id)
    historico = listar_historico_financeiro()
    historico_formatado = formatar_dataframe_para_exibicao(pd.DataFrame(historico))

    assert isinstance(registro["gasto_semana"], float)
    assert isinstance(registro["saldo_atual"], float)
    assert registro["gasto_semana"] == 130
    assert registro["saldo_atual"] == 60.5
    assert historico_formatado.loc[0, "Gasto da semana"] == "R$ 130,00"
    assert historico_formatado.loc[0, "Saldo atual"] == "R$ 60,50"


def test_carregamento_de_frentes_por_id_retorna_dados_corretos(banco_temporario):
    frentes = {frente["nome"]: frente for frente in listar_frentes()}

    carreira = obter_frente(frentes["Carreira / EUA"]["id"])
    doutorado = obter_frente(frentes["Doutorado"]["id"])
    trabalho = obter_frente(frentes["Trabalho / Aulas"]["id"])

    assert carreira["nome"] == "Carreira / EUA"
    assert carreira["objetivo"] != trabalho["objetivo"]
    assert doutorado["nome"] == "Doutorado"
    assert doutorado["objetivo"] != trabalho["objetivo"]
    assert trabalho["nome"] == "Trabalho / Aulas"
    assert trabalho["objetivo"] == "Organizar compromissos profissionais e aulas."


def test_atualizar_frente_por_id_altera_somente_trabalho_aulas(banco_temporario):
    frentes = {frente["nome"]: frente for frente in listar_frentes()}
    trabalho_id = frentes["Trabalho / Aulas"]["id"]
    carreira_id = frentes["Carreira / EUA"]["id"]

    atualizar_frente(
        trabalho_id,
        "Trabalho / Aulas",
        frentes["Trabalho / Aulas"]["objetivo"],
        "manutenção",
        frentes["Trabalho / Aulas"]["importancia"],
        frentes["Trabalho / Aulas"]["minimo_semanal_minutos"],
        frentes["Trabalho / Aulas"]["limite_alerta_dias"],
    )

    assert obter_frente(trabalho_id)["status"] == "manutenção"
    assert obter_frente(carreira_id)["status"] == frentes["Carreira / EUA"]["status"]


def test_nome_duplicado_em_frente_eh_bloqueado_sem_integrity_error(banco_temporario):
    frentes = {frente["nome"]: frente for frente in listar_frentes()}
    trabalho = frentes["Trabalho / Aulas"]

    with pytest.raises(NomeFrenteDuplicadoError, match="Já existe outra frente"):
        atualizar_frente(
            trabalho["id"],
            "Carreira / EUA",
            trabalho["objetivo"],
            trabalho["status"],
            trabalho["importancia"],
            trabalho["minimo_semanal_minutos"],
            trabalho["limite_alerta_dias"],
        )

    assert obter_frente(trabalho["id"])["nome"] == "Trabalho / Aulas"


def test_fluxo_minimo_mvp_persiste_dados_apos_reabrir_conexao(banco_temporario):
    frente_id = {frente["nome"]: frente for frente in listar_frentes()}["Trabalho / Aulas"]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 10, 7, "moderada", "fluxo mínimo")
    tarefa_id = criar_tarefa(semana_id, frente_id, "Preparar aula", "", 60, "2026-06-20", "alta")

    atualizar_status_tarefa(tarefa_id, "concluída", frente_id)
    salvar_financas(semana_id, 130, 60.5, "Mercado", False, "fluxo")
    registrar_progresso(semana_id, frente_id, 45, "Aula preparada", "2026-06-20")
    criar_bloco(semana_id, "2026-06-20", "09:00", "10:00", "trabalho", "Bloco teste", "média", "")

    semana = obter_semana_atual()
    tarefas = listar_tarefas(semana_id=semana_id)
    financas = obter_financas_semana(semana_id)
    progresso = listar_progresso(semana_id)
    blocos = listar_blocos(semana_id)

    assert semana["id"] == semana_id
    assert tarefas[0]["status"] == "concluída"
    assert financas["gasto_semana"] == 130
    assert progresso[0]["resumo_acao"] == "Aula preparada"
    assert blocos[0]["titulo"] == "Bloco teste"


def test_orcamento_registra_despesa_e_calcula_cashflow(banco_temporario):
    frente_id = {frente["nome"]: frente for frente in listar_frentes()}["Finanças"]["id"]
    semana_id = criar_ou_atualizar_semana("2026-06-15", frente_id, 10, 7, "moderada", "orçamento")
    salvar_financas(semana_id, 0, 500, "", False, "")

    registrar_despesa(130, "Mercado", "2026-06-20")
    resumo = obter_resumo_orcamento()
    recentes = listar_despesas_recentes()

    assert resumo["saldo_atual"] == 500
    assert resumo["gasto_semana"] == 130
    assert resumo["margem_livre"] == 370
    assert recentes[0]["categoria"] == "Mercado"
    assert list(recentes[0].keys()) == ["data", "categoria", "valor"]


def test_banco_tem_tabela_lancamentos_financeiros(banco_temporario):
    tabelas = database.fetch_all(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'lancamentos_financeiros'"
    )
    assert tabelas == [{"name": "lancamentos_financeiros"}]
