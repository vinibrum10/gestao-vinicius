from __future__ import annotations

from src.database import execute, fetch_one

FRENTES_INICIAIS = [
    ("Carreira / EUA", "Construir caminho profissional para oportunidades nos EUA.", 5, 90, 10),
    ("Doutorado", "Manter avanço consistente em pesquisa e entregas acadêmicas.", 5, 120, 10),
    ("Inglês / TOEFL", "Evoluir inglês e preparação para TOEFL.", 4, 120, 7),
    ("Finanças", "Acompanhar gastos, saldo e decisões financeiras.", 5, 30, 7),
    ("Programação / Tecnologia", "Desenvolver capacidade técnica e projetos próprios.", 4, 120, 14),
    ("Rotina / Equilíbrio", "Proteger saúde, descanso e organização pessoal.", 4, 90, 7),
    ("Trabalho / Aulas", "Organizar compromissos profissionais e aulas.", 4, 60, 7),
    ("Acompanhamentos", "Manter pendências e conversas importantes sob controle.", 3, 30, 14),
]


def seed_initial_data() -> None:
    for nome, objetivo, importancia, minimo, limite in FRENTES_INICIAIS:
        if not fetch_one("SELECT id FROM frentes WHERE nome = ?", (nome,)):
            execute(
                """
                INSERT INTO frentes
                (nome, objetivo, status, importancia, minimo_semanal_minutos, limite_alerta_dias)
                VALUES (?, ?, 'ativa', ?, ?, ?)
                """,
                (nome, objetivo, importancia, minimo, limite),
            )
