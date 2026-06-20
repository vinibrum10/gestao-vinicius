from __future__ import annotations

from datetime import date

from src.calculations import calcular_divida_atencao
from src.database import execute, fetch_all, fetch_one

STATUS_FRENTES = ["ativa", "manutenção", "pausada", "crítica", "concluída"]


class NomeFrenteDuplicadoError(ValueError):
    pass


def listar_frentes() -> list[dict]:
    frentes = fetch_all("SELECT * FROM frentes ORDER BY importancia DESC, nome")
    for frente in frentes:
        frente.update(
            calcular_divida_atencao(
                frente.get("ultima_acao_data"),
                frente.get("limite_alerta_dias"),
                frente.get("status", "ativa"),
            )
        )
    return frentes


def obter_frente(frente_id: int) -> dict | None:
    return fetch_one("SELECT * FROM frentes WHERE id = ?", (frente_id,))


def criar_frente(nome: str, objetivo: str, status: str, importancia: int, minimo: int, limite: int) -> int:
    nome = nome.strip()
    if fetch_one("SELECT id FROM frentes WHERE nome = ?", (nome,)):
        raise NomeFrenteDuplicadoError("Já existe uma frente com esse nome.")
    return execute(
        """
        INSERT INTO frentes (nome, objetivo, status, importancia, minimo_semanal_minutos, limite_alerta_dias)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nome, objetivo, status, importancia, minimo, limite),
    )


def atualizar_frente(frente_id: int, nome: str, objetivo: str, status: str, importancia: int, minimo: int, limite: int) -> None:
    nome = nome.strip()
    duplicada = fetch_one("SELECT id FROM frentes WHERE nome = ? AND id <> ?", (nome, frente_id))
    if duplicada:
        raise NomeFrenteDuplicadoError("Já existe outra frente com esse nome.")
    execute(
        """
        UPDATE frentes
        SET nome = ?, objetivo = ?, status = ?, importancia = ?, minimo_semanal_minutos = ?,
            limite_alerta_dias = ?, atualizada_em = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (nome, objetivo, status, importancia, minimo, limite, frente_id),
    )


def registrar_acao_frente(frente_id: int, data_acao: str | None = None) -> None:
    execute(
        "UPDATE frentes SET ultima_acao_data = ?, atualizada_em = CURRENT_TIMESTAMP WHERE id = ?",
        (data_acao or date.today().isoformat(), frente_id),
    )
