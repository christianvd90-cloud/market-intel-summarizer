"""
Puente entre tu monitor de order book / funding rate / open interest
y este servicio.

TODO (tuyo): reemplaza `load_latest_snapshot` para que lea el archivo
o base de datos real donde tu monitor guarda los datos.
"""

import os
from datetime import datetime, timezone
from app.models import MarketSnapshot

DATA_SOURCE = os.environ.get("MARKET_DATA_SOURCE", "mock")


def load_latest_snapshot(symbol: str) -> MarketSnapshot:
    if DATA_SOURCE == "mock":
        return _mock_snapshot(symbol)

    if DATA_SOURCE == "json_file":
        return _load_from_json_file(symbol)

    raise NotImplementedError(
        f"MARKET_DATA_SOURCE='{DATA_SOURCE}' no esta implementado todavia."
    )


def _mock_snapshot(symbol: str) -> MarketSnapshot:
    return MarketSnapshot(
        symbol=symbol,
        timestamp=datetime.now(timezone.utc).isoformat(),
        funding_rate=0.00012,
        open_interest=1_250_000_000.0,
        order_book_imbalance=1.18,
        price=68450.0,
        price_change_24h_pct=2.3,
    )


def _load_from_json_file(symbol: str) -> MarketSnapshot:
    import json

    path = os.environ.get("MARKET_DATA_PATH", "./data/latest_snapshot.json")
    with open(path, "r") as f:
        raw = json.load(f)

    return MarketSnapshot(**raw[symbol])
