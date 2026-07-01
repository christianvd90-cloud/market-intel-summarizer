import pytest
from pydantic import ValidationError
from app.models import MarketSnapshot, MarketSummaryResponse


def test_market_snapshot_valid():
    snapshot = MarketSnapshot(
        symbol="BTCUSDT",
        timestamp="2026-07-01T12:00:00Z",
        funding_rate=0.0001,
        open_interest=1_000_000.0,
        order_book_imbalance=1.1,
        price=68000.0,
        price_change_24h_pct=1.5,
    )
    assert snapshot.symbol == "BTCUSDT"


def test_market_snapshot_requires_symbol_and_timestamp():
    with pytest.raises(ValidationError):
        MarketSnapshot(funding_rate=0.0001)


def test_market_summary_response_shape():
    snapshot = MarketSnapshot(symbol="INJUSDT", timestamp="2026-07-01T12:00:00Z")
    response = MarketSummaryResponse(
        symbol="INJUSDT",
        bias="neutral",
        summary="Mercado sin sesgo claro.",
        key_signals=["Funding rate cercano a cero"],
        raw_snapshot=snapshot,
    )
    assert response.bias in ("alcista", "bajista", "neutral")
    assert len(response.key_signals) == 1
