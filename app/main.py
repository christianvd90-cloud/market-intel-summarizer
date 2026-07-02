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
    symbol_clean = symbol.upper()
    try:
        snapshot = load_latest_snapshot(symbol_clean)
        return get_market_interpretation(snapshot)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos disponibles hoy para '{symbol_clean}'. "
                   f"Verifica que el simbolo sea correcto y que el monitor este activo.",
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando resumen: {type(e).__name__}")
