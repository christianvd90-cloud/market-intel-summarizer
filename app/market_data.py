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
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from app.models import MarketSnapshot

DATA_SOURCE = os.environ.get("MARKET_DATA_SOURCE", "mock")

# Tolerancia maxima (segundos) para considerar valido un registro como
# referencia de "hace 24h". Si no hay ningun dato dentro de esta ventana,
# price_change_24h_pct queda en None en vez de usar un dato poco confiable.
TOLERANCIA_24H_SEGUNDOS = 1800  # 30 minutos


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
    cloud_storage = os.path.expanduser("~/Library/CloudStorage")
    if not os.path.isdir(cloud_storage):
        return None
    for entry in os.listdir(cloud_storage):
        if entry.startswith("GoogleDrive-"):
            candidate = os.path.join(cloud_storage, entry, "Mi unidad", "orderbook_data")
            if os.path.isdir(candidate):
                return candidate
    return None


def _to_float(value) -> Optional[float]:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def _find_price_24h_ago(gdrive_path, symbol_clean, current_ts):
    objetivo = current_ts - timedelta(hours=24)
    candidatos = []
    for offset_dias in (1, 0):
        fecha = (current_ts - timedelta(days=offset_dias)).strftime("%Y%m%d")
        path = Path(gdrive_path) / f"orderbook_{symbol_clean}_{fecha}.csv"
        if not path.exists():
            continue
        with open(path, "r", newline="") as f:
            for row in csv.DictReader(f):
                ts_str = row.get("ts")
                if not ts_str:
                    continue
                try:
                    ts = datetime.fromisoformat(ts_str)
                except ValueError:
                    continue
                diff = abs((ts - objetivo).total_seconds())
                candidatos.append((diff, row.get("mid_price")))
    if not candidatos:
        return None
    diferencia_segundos, mid_price = min(candidatos, key=lambda x: x[0])
    if diferencia_segundos > TOLERANCIA_24H_SEGUNDOS:
        return None
    return _to_float(mid_price)


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
    current_ts = datetime.fromisoformat(last["ts"])
    current_price = _to_float(last.get("mid_price"))

    price_24h_ago = _find_price_24h_ago(gdrive_path, symbol_clean, current_ts)
    price_change_24h_pct = None
    if price_24h_ago and current_price:
        price_change_24h_pct = round(
            ((current_price - price_24h_ago) / price_24h_ago) * 100, 4
        )

    return MarketSnapshot(
        symbol=symbol_clean,
        timestamp=last["ts"],
        funding_rate=_to_float(last.get("funding")),
        open_interest=_to_float(last.get("oi")),
        order_book_imbalance=_to_float(last.get("imbalance")),
        price=current_price,
        price_change_24h_pct=price_change_24h_pct,
    )
