from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TIMEZONE = ZoneInfo("America/Sao_Paulo")


class GoogleCalendarConfigError(FileNotFoundError):
    pass


def _carregar_credenciais() -> Credentials:
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not CREDENTIALS_PATH.exists():
            raise GoogleCalendarConfigError(
                "Arquivo credentials.json não encontrado na raiz do projeto."
            )
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _servico_calendar():
    creds = _carregar_credenciais()
    return build("calendar", "v3", credentials=creds)


def _inicio_dia(data_ref: date) -> datetime:
    return datetime.combine(data_ref, time.min, tzinfo=TIMEZONE)


def _fim_dia(data_ref: date) -> datetime:
    return datetime.combine(data_ref, time.max, tzinfo=TIMEZONE)


def obter_eventos_semana(data_inicio: date, data_fim: date) -> list[dict[str, Any]]:
    servico = _servico_calendar()
    resultado = (
        servico.events()
        .list(
            calendarId="primary",
            timeMin=_inicio_dia(data_inicio).isoformat(),
            timeMax=_fim_dia(data_fim).isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    eventos = []
    for item in resultado.get("items", []):
        inicio = item.get("start", {})
        fim = item.get("end", {})
        eventos.append(
            {
                "id": item.get("id"),
                "titulo": item.get("summary", "Sem título"),
                "inicio": inicio.get("dateTime") or inicio.get("date"),
                "fim": fim.get("dateTime") or fim.get("date"),
                "dia_inteiro": "date" in inicio,
                "status": item.get("status"),
            }
        )
    return eventos
