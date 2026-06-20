from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "gestao_vinicius.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def fetch_all(query: str, params: Iterable | None = None) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(query, tuple(params or ())).fetchall()
        return [dict(row) for row in rows]


def fetch_one(query: str, params: Iterable | None = None) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(query, tuple(params or ())).fetchone()
        return dict(row) if row else None


def execute(query: str, params: Iterable | None = None) -> int:
    with get_connection() as conn:
        cursor = conn.execute(query, tuple(params or ()))
        conn.commit()
        return int(cursor.lastrowid)


def init_db() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS frentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                objetivo TEXT,
                status TEXT NOT NULL DEFAULT 'ativa',
                importancia INTEGER NOT NULL DEFAULT 3,
                minimo_semanal_minutos INTEGER NOT NULL DEFAULT 60,
                limite_alerta_dias INTEGER NOT NULL DEFAULT 14,
                ultima_acao_data TEXT,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS semanas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio TEXT NOT NULL UNIQUE,
                data_fim TEXT NOT NULL,
                foco_principal_frente_id INTEGER,
                tempo_livre_estimado_horas REAL DEFAULT 0,
                tempo_livre_util_horas REAL DEFAULT 0,
                peso_semana TEXT DEFAULT 'normal',
                observacoes TEXT,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (foco_principal_frente_id) REFERENCES frentes(id)
            );

            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semana_id INTEGER NOT NULL,
                frente_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                tempo_estimado_minutos INTEGER DEFAULT 30,
                data_planejada TEXT,
                status TEXT NOT NULL DEFAULT 'pendente',
                prioridade TEXT DEFAULT 'média',
                concluida_em TEXT,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (semana_id) REFERENCES semanas(id),
                FOREIGN KEY (frente_id) REFERENCES frentes(id)
            );

            CREATE TABLE IF NOT EXISTS financas_semanais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semana_id INTEGER NOT NULL UNIQUE,
                gasto_semana REAL NOT NULL DEFAULT 0,
                saldo_atual REAL NOT NULL DEFAULT 0,
                categoria_mais_pesada TEXT,
                teve_gasto_inesperado INTEGER NOT NULL DEFAULT 0,
                observacoes TEXT,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (semana_id) REFERENCES semanas(id)
            );

            CREATE TABLE IF NOT EXISTS blocos_tempo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semana_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fim TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'outro',
                titulo TEXT NOT NULL,
                nivel_energia TEXT DEFAULT 'média',
                observacoes TEXT,
                FOREIGN KEY (semana_id) REFERENCES semanas(id)
            );

            CREATE TABLE IF NOT EXISTS progresso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semana_id INTEGER NOT NULL,
                frente_id INTEGER NOT NULL,
                minutos_realizados INTEGER NOT NULL DEFAULT 0,
                resumo_acao TEXT NOT NULL,
                data_acao TEXT NOT NULL,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (semana_id) REFERENCES semanas(id),
                FOREIGN KEY (frente_id) REFERENCES frentes(id)
            );
            """
        )
        conn.commit()
