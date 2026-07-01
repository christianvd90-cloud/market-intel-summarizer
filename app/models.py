"""
Esquemas de datos (Pydantic) para el servicio.
"""

from pydantic import BaseModel, Field
from typing import Optional


class MarketSnapshot(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    timestamp: str = Field(..., description="ISO 8601, ej: 2026-07-01T12:00:00Z")
    funding_rate: Optional[float] = Field(None, description="Funding rate actual, ej: 0.0001")
    open_interest: Optional[float] = Field(None, description="Open interest en contratos")
    order_book_imbalance: Optional[float] = Field(
        None,
        description=(
            "OBI normalizado en rango [0, 1] = vol_bids_top / (vol_bids_top + vol_asks_top). "
            "1.0 = dominio total de bids (presion compradora), 0.5 = equilibrio, "
            "0.0 = dominio total de asks (presion vendedora)."
        ),
    )
    price: Optional[float] = Field(None, description="Precio spot/futuro actual (mid_price)")
    price_change_24h_pct: Optional[float] = Field(None)


class MarketSummaryResponse(BaseModel):
    symbol: str
    bias: str = Field(..., description="'alcista', 'bajista' o 'neutral'")
    summary: str = Field(..., description="Resumen en lenguaje natural")
    key_signals: list[str] = Field(default_factory=list)
    raw_snapshot: MarketSnapshot
