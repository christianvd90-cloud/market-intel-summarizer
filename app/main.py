"""
Market Intelligence Summarizer - API FastAPI
"""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException  # noqa: E402
from app.models import MarketSummaryResponse  # noqa: E402
from app.market_data import load_latest_snapshot  # noqa: E402
from app.llm_client import get_market_interpretation  # noqa: E402

app = FastAPI(
    title="Market Intelligence Summarizer",
    description="Interpreta snapshots de mercado cripto usando un LLM.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/market-summary/{symbol}", response_model=MarketSummaryResponse)
def market_summary(symbol: str):
    try:
        snapshot = load_latest_snapshot(symbol.upper())
        return get_market_interpretation(snapshot)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen: {e}")
