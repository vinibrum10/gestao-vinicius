from __future__ import annotations

from datetime import date, datetime


def formatar_data_br(valor: str | date | None) -> str:
    if not valor:
        return ""
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    texto = str(valor)[:10]
    formatos = ("%Y-%m-%d", "%Y/%m/%d")
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return str(valor)


def formatar_intervalo_br(data_inicio: str | date | None, data_fim: str | date | None) -> str:
    inicio = formatar_data_br(data_inicio)
    fim = formatar_data_br(data_fim)
    if inicio and fim:
        return f"{inicio} a {fim}"
    return inicio or fim
