"""
Cliente para consultar al LLM (Claude) y pedirle que interprete
un snapshot de mercado.

SEGURIDAD: la API key se lee siempre desde variable de entorno.
"""

import os
import json
import re
from anthropic import Anthropic
from app.models import MarketSnapshot, MarketSummaryResponse

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Falta ANTHROPIC_API_KEY en el entorno. "
        "Copia .env.example a .env y completalo (nunca subas .env a Git)."
    )

client = Anthropic(api_key=API_KEY)

SYSTEM_PROMPT = """Eres un analista cuantitativo especializado en mercados de futuros cripto.
Recibes un snapshot de datos de mercado (funding rate, open interest, order book imbalance)
y debes interpretarlo de forma concisa y accionable.

Responde SIEMPRE con JSON valido puro, SIN bloques de markdown (nada de ```json),
sin texto antes ni despues, con esta forma exacta:
{
  "bias": "alcista" | "bajista" | "neutral",
  "summary": "resumen de 2-3 frases en espanol, tono profesional, listo para un reporte",
  "key_signals": ["senal 1", "senal 2"]
}
"""


def build_user_prompt(snapshot: MarketSnapshot) -> str:
    return f"""Snapshot de mercado para {snapshot.symbol} ({snapshot.timestamp}):
- Funding rate: {snapshot.funding_rate}
- Open interest: {snapshot.open_interest}
- Order book imbalance (bid/ask): {snapshot.order_book_imbalance}
- Precio: {snapshot.price}
- Variacion 24h: {snapshot.price_change_24h_pct}%

Interpreta estos datos y responde en el formato JSON indicado."""


def _clean_json_response(raw_text: str) -> str:
    """
    Algunos modelos envuelven el JSON en bloques de markdown
    (```json ... ```) aunque se les pida no hacerlo. Esta funcion
    limpia eso antes de intentar parsear.
    """
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def get_market_interpretation(snapshot: MarketSnapshot) -> MarketSummaryResponse:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(snapshot)}],
    )

    raw_text = response.content[0].text
    cleaned_text = _clean_json_response(raw_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError:
        raise ValueError(f"El LLM no devolvio JSON valido: {raw_text[:300]}")

    return MarketSummaryResponse(
        symbol=snapshot.symbol,
        bias=parsed["bias"],
        summary=parsed["summary"],
        key_signals=parsed.get("key_signals", []),
        raw_snapshot=snapshot,
    )
