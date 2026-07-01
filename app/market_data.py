"""
Puente entre tu monitor de order book / funding rate / open interest
(orderbook_monitor_v4.py) y este servicio.

Los CSV se generan con formato: orderbook_{SIMBOLO}_{YYYYMMDD}.csv
Columnas reales: ts,activo,mid_price,best_bid,best_ask,spread_pct,imbalance,
vol_bids_top,vol_asks_top,microprice,wall_bid_px,wall_bid_qty,wall_ask_px,
wall_ask_qty,oi,oi_value,funding,mark_price,basis_pct
"""

import os
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from app.models import MarketSnapshot

DATA_SOURCE = os.environ.get("MARKET_DATA_SOURCE", "mock")


def load_latest_snapshot(symbol: str) -> MarketSnapshot:
    if DATA_SOURCE == "mock":
        return _mock_snapshot(symbol)

    if DATA_SOURCE == "gdrive_csv":
        return _load_from_gdrive_csv(symbol)

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


def _detect_gdrive_orderbook_path() -> Optional[str]:
    """
    Busca automaticamente la carpeta de Google Drive sincronizada,
    sin hardcodear el email del usuario en el codigo (ese dato no
    debe quedar expuesto en un repositorio publico).
    """
    cloud_storage = os.path.expanduser("~/Library/CloudStorage")
    if not os.path.isdir(cloud_storage):
        return None

    for entry in os.listdir(cloud_storage):
        if entry.startswith("GoogleDrive-"):
            candidate = os.path.join(cloud_storage, entry, "Mi unidad", "orderbook_data")
            if os.path.isdir(candidate):
                return candidate

    return None


def _load_from_gdrive_csv(symbol: str) -> MarketSnapshot:
    gdrive_path = os.environ.get("GDRIVE_ORDERBOOK_PATH") or _detect_gdrive_orderbook_path()

    if not gdrive_path:
        raise FileNotFoundError(
            "No se encontro la carpeta de orderbook_data en Google Drive. "
            "Define GDRIVE_ORDERBOOK_PATH en tu .env con la ruta exacta."
        )

    symbol_clean = symbol.upper().replace("/", "")
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"orderbook_{symbol_clean}_{today}.csv"
    path = Path(gdrive_path) / filename

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de hoy: {path}. "
            "Verifica que orderbook_monitor_v4.py este corriendo hoy."
        )

    with open(path, "r", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError(f"El archivo {path} existe pero no tiene filas todavia.")

    last = rows[-1]

    def _to_float(value):
        try:
            return float(value) if value not in (None, "") else None
        except ValueError:
            return None

    return MarketSnapshot(
        symbol=symbol_clean,
        timestamp=last["ts"],
        funding_rate=_to_float(last.get("funding")),
        open_interest=_to_float(last.get("oi")),
        order_book_imbalance=_to_float(last.get("imbalance")),
        price=_to_float(last.get("mid_price")),
        price_change_24h_pct=None,
    )
