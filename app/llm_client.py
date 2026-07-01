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
Recibes un snapshot de datos de mercado y debes interpretarlo de forma concisa y accionable.

Definiciones exactas de los campos que recibiras:
- order_book_imbalance (OBI): normalizado en [0, 1] = vol_bids_top / (vol_bids_top + vol_asks_top).
  1.0 = bids dominan (presion compradora), 0.5 = equilibrio, 0.0 = asks dominan (presion vendedora).
  Los umbrales relevantes son >0.60 (sesgo comprador) y <0.40 (sesgo vendedor); la zona 0.40-0.60
  se considera neutral/ruido.
- funding_rate: tasa de financiamiento del perpetuo. Positivo = predominio de posiciones largas.
- open_interest: contratos abiertos totales, indica participacion/liquidez del mercado.

Advertencia importante que debes tener en cuenta al interpretar el imbalance: es una señal de
INTENCION en el libro de ordenes, no de ejecucion. Ordenes grandes pueden colocarse y retirarse
antes de ejecutarse (spoofing/layering), especialmente en cripto. Si el imbalance es extremo
(cercano a 0 o 1) pero no hay otras señales que lo corroboren (funding, variacion de precio),
menciona esta cautela brevemente en el resumen en vez de tratarlo como señal definitiva.

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
- Order book imbalance (OBI, escala 0-1): {snapshot.order_book_imbalance}
- Precio (mid): {snapshot.price}
- Variacion 24h: {snapshot.price_change_24h_pct}%

Interpreta estos datos y responde en el formato JSON indicado."""


def _clean_json_response(raw_text: str) -> str:
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
