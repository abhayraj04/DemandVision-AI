"""
MarketVision AI - FastAPI API Endpoints Router
Implements high-performance, validated REST endpoints for institutional market intelligence.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np

from backend.preprocessing.data_pipeline import STOCKS_METADATA, INDICES_METADATA
from backend.features.technical_indicators import (
    generate_analytical_signals, indicator_catalog_metadata
)
from backend.risk.risk_engine import (
    simulate_portfolio_risk, risk_metrics_educational_metadata
)

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FEATURES_DIR = os.path.join(DATA_DIR, "features")
PREDICTIONS_DIR = os.path.join(DATA_DIR, "predictions")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

# In-memory cache for ultra-low latency response
_DATA_CACHE = {}


def load_processed_data(symbol: str) -> pd.DataFrame:
    """Loads and caches processed parquet DataFrame."""
    key = f"proc_{symbol}"
    if key not in _DATA_CACHE:
        file_path = os.path.join(PROCESSED_DIR, f"{symbol}.parquet")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Data for instrument '{symbol}' not found")
        _DATA_CACHE[key] = pd.read_parquet(file_path)
    return _DATA_CACHE[key]


def load_features_data(symbol: str) -> pd.DataFrame:
    """Loads and caches feature parquet DataFrame."""
    key = f"feat_{symbol}"
    if key not in _DATA_CACHE:
        file_path = os.path.join(FEATURES_DIR, f"{symbol}_features.parquet")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Features for instrument '{symbol}' not found")
        _DATA_CACHE[key] = pd.read_parquet(file_path)
    return _DATA_CACHE[key]


# Pydantic Request Models
class PortfolioAnalyzeRequest(BaseModel):
    weights: Dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"RELIANCE": 0.25, "TCS": 0.25, "HDFCBANK": 0.25, "INFY": 0.25}},
        description="Dictionary mapping ticker symbols to portfolio percentage or decimal weights"
    )
    risk_free_rate: Optional[float] = Field(default=0.065, description="Annualized risk-free rate")


# 1. GET /api/health
@router.get("/health", tags=["System"])
def get_health_status():
    """Health check endpoint providing system status and environment details."""
    return {
        "status": "online",
        "service": "MarketVision AI Institutional Engine",
        "version": "1.0.0",
        "supported_stocks_count": len(STOCKS_METADATA),
        "data_mode": "Historical Certified NSE Feeds",
        "live_market_disclaimer": "All market metrics are computed from historical and delayed NSE datasets. Not a live execution gateway."
    }


# 2. GET /api/market/overview
@router.get("/market/overview", tags=["Market"])
def get_market_overview():
    """Returns top-level market snapshot across major NSE indices and top movers."""
    indices_summary = []
    
    for idx_name, meta in INDICES_METADATA.items():
        safe_sym = idx_name.replace(" ", "_")
        try:
            df = load_processed_data(safe_sym)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            change = float(latest["close"] - prev["close"])
            pct_change = float(latest["daily_return"] * 100.0)

            indices_summary.append({
                "index_name": idx_name,
                "symbol": meta["raw_symbol"],
                "sector": meta["sector"],
                "latest_close": round(float(latest["close"]), 2),
                "open": round(float(latest["open"]), 2),
                "high": round(float(latest["high"]), 2),
                "low": round(float(latest["low"]), 2),
                "change": round(change, 2),
                "percent_change": round(pct_change, 2),
                "volume": float(latest["volume"]),
                "last_timestamp": latest["datetime_str"],
                "trend": "Bullish" if pct_change > 0.1 else ("Bearish" if pct_change < -0.1 else "Neutral")
            })
        except Exception as e:
            logger.error(f"Error loading index {idx_name}: {e}")

    # Top Gaining and Losing Equities
    stock_movers = []
    for sym, meta in STOCKS_METADATA.items():
        try:
            df = load_processed_data(sym)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            pct_change = float(latest["daily_return"] * 100.0)

            stock_movers.append({
                "symbol": sym,
                "name": meta["name"],
                "sector": meta["sector"],
                "latest_price": round(float(latest["close"]), 2),
                "change_percent": round(pct_change, 2),
                "volume": float(latest["volume"]),
                "last_updated": latest["datetime_str"]
            })
        except Exception:
            continue

    sorted_movers = sorted(stock_movers, key=lambda x: x["change_percent"], reverse=True)
    top_gainers = sorted_movers[:3]
    top_losers = sorted_movers[-3:]

    # Overall Market Sentiment Index
    nifty_obj = next((item for item in indices_summary if item["index_name"] == "NIFTY 50"), None)
    nifty_pct = nifty_obj["percent_change"] if nifty_obj else 0.0
    sentiment = "Bullish" if nifty_pct > 0.3 else ("Bearish" if nifty_pct < -0.3 else "Consolidating")

    return {
        "timestamp_status": "Latest Historical Dataset Session (Historical Market Analytics)",
        "market_sentiment": sentiment,
        "indices": indices_summary,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "watchlist_symbols": list(STOCKS_METADATA.keys())
    }


# 3. GET /api/stocks
@router.get("/stocks", tags=["Stocks"])
def list_supported_stocks():
    """Lists all supported NSE equities with current quote summaries and sector classification."""
    stocks_list = []
    for sym, meta in STOCKS_METADATA.items():
        try:
            df = load_processed_data(sym)
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # 52-week high & low (252 bars)
            recent_252 = df.iloc[-252:] if len(df) >= 252 else df
            high_52w = float(recent_252["high"].max())
            low_52w = float(recent_252["low"].min())

            stocks_list.append({
                "symbol": sym,
                "ticker": meta["ticker"],
                "name": meta["name"],
                "sector": meta["sector"],
                "benchmark": meta["benchmark"],
                "latest_close": round(float(latest["close"]), 2),
                "change": round(float(latest["close"] - prev["close"]), 2),
                "change_percent": round(float(latest["daily_return"] * 100.0), 2),
                "volume": float(latest["volume"]),
                "high_52w": round(high_52w, 2),
                "low_52w": round(low_52w, 2),
                "last_traded_date": latest["datetime_str"]
            })
        except Exception as e:
            logger.error(f"Error loading stock {sym}: {e}")

    return {
        "count": len(stocks_list),
        "stocks": stocks_list
    }


# 4. GET /api/stocks/{symbol}
@router.get("/stocks/{symbol}", tags=["Stocks"])
def get_stock_profile(symbol: str):
    """Returns detailed asset profile and financial metrics for a specific stock."""
    sym = symbol.upper().replace(".NS", "")
    if sym not in STOCKS_METADATA:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not supported")

    meta = STOCKS_METADATA[sym]
    df = load_processed_data(sym)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    recent_252 = df.iloc[-252:] if len(df) >= 252 else df
    high_52w = float(recent_252["high"].max())
    low_52w = float(recent_252["low"].min())

    ann_vol = float(df["daily_return"].std() * np.sqrt(252) * 100.0)

    return {
        "symbol": sym,
        "name": meta["name"],
        "sector": meta["sector"],
        "benchmark": meta["benchmark"],
        "quote": {
            "current_price": round(float(latest["close"]), 2),
            "open": round(float(latest["open"]), 2),
            "high": round(float(latest["high"]), 2),
            "low": round(float(latest["low"]), 2),
            "change": round(float(latest["close"] - prev["close"]), 2),
            "change_percent": round(float(latest["daily_return"] * 100.0), 2),
            "volume": float(latest["volume"]),
            "last_date": latest["datetime_str"]
        },
        "performance": {
            "52_week_high": round(high_52w, 2),
            "52_week_low": round(low_52w, 2),
            "annualized_volatility": round(ann_vol, 2),
            "total_bars_available": len(df)
        }
    }


# 5. GET /api/stocks/{symbol}/history
@router.get("/stocks/{symbol}/history", tags=["Stocks"])
def get_stock_history(
    symbol: str,
    limit: Optional[int] = Query(default=250, ge=10, le=2000, description="Number of bars to return (default 250 ~ 1 trading year)")
):
    """Returns historical OHLCV candlestick series formatted for TradingView and Recharts."""
    sym = symbol.upper().replace(" ", "_").replace(".NS", "")
    df = load_processed_data(sym)

    sub_df = df.iloc[-limit:] if limit and len(df) > limit else df

    candles = []
    for _, row in sub_df.iterrows():
        candles.append({
            "time": row["datetime_str"],
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": float(row["volume"]),
            "daily_return": round(float(row["daily_return"] * 100.0), 2)
        })

    return {
        "symbol": sym,
        "count": len(candles),
        "start_date": candles[0]["time"] if candles else None,
        "end_date": candles[-1]["time"] if candles else None,
        "data": candles
    }


# 6. GET /api/stocks/{symbol}/indicators
@router.get("/stocks/{symbol}/indicators", tags=["Technical Analysis"])
def get_stock_indicators(
    symbol: str,
    limit: Optional[int] = Query(default=120, ge=30, le=500, description="Recent bars with indicator values")
):
    """Returns technical indicator time-series, active analytical signals, and indicator metadata."""
    sym = symbol.upper().replace(" ", "_").replace(".NS", "")
    df_feat = load_features_data(sym)

    sub_df = df_feat.iloc[-limit:] if limit and len(df_feat) > limit else df_feat

    series_data = []
    for _, row in sub_df.iterrows():
        series_data.append({
            "date": row["datetime_str"],
            "close": round(float(row["close"]), 2),
            "sma_20": round(float(row["sma_20"]), 2) if pd.notna(row["sma_20"]) else None,
            "sma_50": round(float(row["sma_50"]), 2) if pd.notna(row["sma_50"]) else None,
            "sma_200": round(float(row["sma_200"]), 2) if pd.notna(row["sma_200"]) else None,
            "ema_9": round(float(row["ema_9"]), 2) if pd.notna(row["ema_9"]) else None,
            "ema_21": round(float(row["ema_21"]), 2) if pd.notna(row["ema_21"]) else None,
            "rsi_14": round(float(row["rsi_14"]), 2) if pd.notna(row["rsi_14"]) else None,
            "macd": round(float(row["macd"]), 2) if pd.notna(row["macd"]) else None,
            "macd_signal": round(float(row["macd_signal"]), 2) if pd.notna(row["macd_signal"]) else None,
            "macd_hist": round(float(row["macd_hist"]), 2) if pd.notna(row["macd_hist"]) else None,
            "bb_upper": round(float(row["bb_upper"]), 2) if pd.notna(row["bb_upper"]) else None,
            "bb_middle": round(float(row["bb_middle"]), 2) if pd.notna(row["bb_middle"]) else None,
            "bb_lower": round(float(row["bb_lower"]), 2) if pd.notna(row["bb_lower"]) else None,
            "bb_bandwidth": round(float(row["bb_bandwidth"]), 4) if pd.notna(row["bb_bandwidth"]) else None,
            "atr_14": round(float(row["atr_14"]), 2) if pd.notna(row["atr_14"]) else None,
            "obv": float(row["obv"]) if pd.notna(row["obv"]) else None,
        })

    active_signals = generate_analytical_signals(df_feat)
    catalog = indicator_catalog_metadata()

    return {
        "symbol": sym,
        "active_signals": active_signals,
        "indicator_catalog": catalog,
        "history": series_data
    }


# 7. GET /api/stocks/{symbol}/forecast
@router.get("/stocks/{symbol}/forecast", tags=["Forecasting"])
def get_stock_forecast(symbol: str):
    """Returns multi-horizon (7, 14, 30 days) price forecasts, confidence bands, and walk-forward validation."""
    sym = symbol.upper().replace(" ", "_").replace(".NS", "")
    pred_file = os.path.join(PREDICTIONS_DIR, f"{sym}_forecast.json")
    
    if not os.path.exists(pred_file):
        raise HTTPException(status_code=404, detail=f"Forecast package for '{symbol}' not found")

    with open(pred_file, "r") as f:
        pkg = json.load(f)

    return pkg


# 8. GET /api/stocks/{symbol}/risk
@router.get("/stocks/{symbol}/risk", tags=["Risk Intelligence"])
def get_stock_risk(symbol: str):
    """Returns full risk analytics: Volatility, Max Drawdown, VaR, CVaR, Sharpe, Beta, and rolling drawdowns."""
    sym = symbol.upper().replace(" ", "_").replace(".NS", "")
    risk_file = os.path.join(REPORTS_DIR, "risk_analytics.json")
    
    if not os.path.exists(risk_file):
        raise HTTPException(status_code=500, detail="Risk analytics report not generated")

    with open(risk_file, "r") as f:
        profiles = json.load(f)

    if sym not in profiles:
        raise HTTPException(status_code=404, detail=f"Risk profile for '{symbol}' not found")

    meta = risk_metrics_educational_metadata()
    return {
        "profile": profiles[sym],
        "metric_definitions": meta
    }


# 9. POST /api/portfolio/analyze
@router.post("/portfolio/analyze", tags=["Risk Intelligence"])
def analyze_portfolio(req: PortfolioAnalyzeRequest):
    """Simulates multi-asset portfolio risk, diversification benefit, and VaR/CVaR for custom user allocations."""
    if not req.weights:
        raise HTTPException(status_code=400, detail="Portfolio weights dictionary cannot be empty")

    # Validate symbols
    for s in req.weights.keys():
        clean_s = s.upper().replace(".NS", "")
        if clean_s not in STOCKS_METADATA and clean_s != "NIFTY_50":
            raise HTTPException(status_code=400, detail=f"Asset '{s}' not supported in portfolio engine")

    clean_weights = {s.upper().replace(".NS", ""): float(w) for s, w in req.weights.items()}

    try:
        sim_res = simulate_portfolio_risk(clean_weights, req.risk_free_rate or 0.065)
        return sim_res
    except Exception as e:
        logger.error(f"Portfolio simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 10. GET /api/models/performance
@router.get("/models/performance", tags=["Model Performance"])
def get_models_performance():
    """Returns the comprehensive model leaderboard, residual diagnostics, and selection rationales across all assets."""
    leaderboard_file = os.path.join(REPORTS_DIR, "model_leaderboard.json")
    if not os.path.exists(leaderboard_file):
        raise HTTPException(status_code=500, detail="Model leaderboard report not found")

    with open(leaderboard_file, "r") as f:
        board = json.load(f)

    return {
        "leaderboard": board,
        "evaluation_criteria": {
            "primary_metric": "Root Mean Squared Error (RMSE)",
            "secondary_metrics": ["Directional Accuracy (%)", "Mean Absolute Error (MAE)", "R-squared"],
            "leakage_protocol": "Strict Chronological Partitioning (Zero Random Train-Test Shuffling)"
        }
    }


# 11. GET /api/insights/{symbol}
@router.get("/insights/{symbol}", tags=["AI Insights"])
def get_stock_insights(symbol: str):
    """Synthesizes deterministic, quantitative AI market insights directly from computed metrics (ready for LLM)."""
    sym = symbol.upper().replace(" ", "_").replace(".NS", "")
    from backend.insights.insights_engine import generate_asset_insights
    insights = generate_asset_insights(sym)
    return insights
