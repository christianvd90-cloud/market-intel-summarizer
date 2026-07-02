"""
Telegram Notifier — Market Intelligence Summarizer

Consulta periódicamente la API local (FastAPI + LLM) y envía el análisis
de mercado a un chat de Telegram.

Arquitectura:
    [API FastAPI local] --> [Notifier] --> [Telegram Bot API] --> [Tu chat]

Uso:
    python notifier.py                  # una sola consulta y envío, luego termina
    python notifier.py --loop 900       # loop continuo cada 900s (15 min)

SEGURIDAD: token y chat_id se leen siempre desde variables de entorno.
Nunca hardcodear credenciales en este archivo.
"""

import os
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_BASE_URL = os.environ.get("MARKET_API_URL", "http://localhost:8000")
SYMBOLS = [s.strip() for s in os.environ.get("NOTIFIER_SYMBOLS", "BTCUSDT").split(",")]

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise SystemExit(
        "Faltan TELEGRAM_BOT_TOKEN y/o TELEGRAM_CHAT_ID en el entorno. "
        "Revisa tu .env (nunca hardcodees estos valores en el codigo)."
    )

BIAS_EMOJI = {"alcista": "\U0001F7E2", "bajista": "\U0001F534", "neutral": "\u26AA"}


def fetch_market_summary(symbol: str) -> dict | None:
    """Consulta el endpoint /market-summary/{symbol} de la API local."""
    url = f"{API_BASE_URL}/market-summary/{symbol}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo consultar {symbol}: {type(e).__name__}")
        return None


def format_message(data: dict) -> str:
    """Da formato Markdown al análisis para enviarlo a Telegram."""
    emoji = BIAS_EMOJI.get(data["bias"], "\u26AA")
    signals = "\n".join(f"  \u2022 {s}" for s in data.get("key_signals", []))
    return (
        f"{emoji} *{data['symbol']}* \u2014 sesgo {data['bias']}\n\n"
        f"{data['summary']}\n\n"
        f"*Señales clave:*\n{signals}"
    )


def send_telegram_message(text: str) -> bool:
    """Envia un mensaje al chat configurado via la API de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo enviar a Telegram: {type(e).__name__}")
        return False


def run_once():
    """Consulta y notifica cada simbolo configurado, una vez."""
    for symbol in SYMBOLS:
        data = fetch_market_summary(symbol)
        if data:
            sent = send_telegram_message(format_message(data))
            print(f"[{symbol}] {'enviado' if sent else 'FALLO envio'}")
        else:
            print(f"[{symbol}] sin datos disponibles, se omite notificacion")


def main():
    parser = argparse.ArgumentParser(description="Notificador de mercado a Telegram")
    parser.add_argument(
        "--loop", type=int, default=None,
        help="Segundos entre ciclos. Si se omite, corre una vez y termina.",
    )
    args = parser.parse_args()

    if args.loop:
        print(f"Notifier corriendo en loop cada {args.loop}s. Ctrl+C para detener.")
        while True:
            run_once()
            time.sleep(args.loop)
    else:
        run_once()


if __name__ == "__main__":
    main()
