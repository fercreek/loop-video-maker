"""
scripts/yt_auth.py — OAuth 2.0 flow para YouTube Data API + Analytics API.

Uso:
    .venv/bin/python3 scripts/yt_auth.py

Requiere: client_secret.json en la raíz del proyecto.
Genera:   data/yt_token.json  (token persistente, se auto-refresca)

Scopes pedidos:
  - youtube.readonly        → lista de videos, metadata
  - yt-analytics.readonly   → métricas: views, watch time, CTR, retention
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

CLIENT_SECRET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "client_secret.json")
TOKEN_PATH    = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "yt_token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube",           # read + write (update titles, descriptions)
    "https://www.googleapis.com/auth/youtube.force-ssl", # required for comments API
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_credentials() -> Credentials:
    """Load or refresh credentials. Run OAuth flow if no token exists."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                print(f"\n❌ client_secret.json not found at: {CLIENT_SECRET}")
                print("\nPasos:")
                print("  1. https://console.cloud.google.com/")
                print("  2. APIs → YouTube Data API v3 + YouTube Analytics API → Activar")
                print("  3. Credenciales → Crear → OAuth 2.0 → Aplicación de escritorio")
                print("  4. Descargar JSON → guardar como client_secret.json en la raíz del proyecto")
                sys.exit(1)
            print("Abriendo navegador para autorización...")
            print("⚠️  Elige el canal VersiculoDeDios, NO la cuenta personal.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            # prompt= fuerza el selector de cuenta/canal. Sin esto Google reusa la
            # sesión activa y mintea el token contra el canal personal en silencio:
            # la Data API responde normal y solo Analytics falla, con 403 opaco.
            creds = flow.run_local_server(port=0, prompt="select_account consent")

        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"✅ Token guardado en {TOKEN_PATH}")

    return creds


EXPECTED_CHANNEL_ID = "UC2l5TZjHzRtaRjH8kT_yQ2w"  # @VersiculoDeDios


def verify_channel(creds: Credentials) -> bool:
    """Confirma que el token quedó ligado al canal correcto, no a la cuenta personal."""
    from googleapiclient.discovery import build

    ch = build("youtube", "v3", credentials=creds).channels().list(
        part="snippet", mine=True
    ).execute()["items"][0]
    ok = ch["id"] == EXPECTED_CHANNEL_ID
    print(f"\n{'✅' if ok else '❌'} Canal del token: {ch['snippet']['title']} ({ch['id']})")
    if not ok:
        print(f"   Se esperaba {EXPECTED_CHANNEL_ID}. Analytics va a dar 403.")
        print(f"   Fix: rm {TOKEN_PATH} y vuelve a correr, eligiendo VersiculoDeDios.")
    return ok


if __name__ == "__main__":
    creds = get_credentials()
    print(f"\n✅ Autenticado. Token válido hasta: {creds.expiry}")
    if not verify_channel(creds):
        sys.exit(1)
    print("   Siguiente paso: .venv/bin/python3 scripts/yt_stats.py")
