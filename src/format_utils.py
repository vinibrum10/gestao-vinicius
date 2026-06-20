from __future__ import annotations

from decimal import Decimal, InvalidOperation


def formatar_moeda_br(valor: float | int | str | None) -> str:
    if valor is None or valor == "":
        return "R$ 0,00"
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return str(valor)
    texto = f"{numero:,.2f}"
    return f"R$ {texto.replace(',', 'X').replace('.', ',').replace('X', '.')}"
