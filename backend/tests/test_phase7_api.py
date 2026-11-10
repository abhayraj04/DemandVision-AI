"""
Phase 7 Test Suite: FastAPI REST API Endpoints Verification
"""
import os
import sys
import pytest
from starlette.testclient import TestClient

# Ensure root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["supported_stocks_count"] == 10


def test_market_overview():
    res = client.get("/api/market/overview")
    assert res.status_code == 200
    data = res.json()
    assert "indices" in data
    assert len(data["indices"]) >= 4
    assert "top_gainers" in data
    assert "top_losers" in data


def test_stocks_list():
    res = client.get("/api/stocks")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 10
    symbols = [s["symbol"] for s in data["stocks"]]
    assert "RELIANCE" in symbols
    assert "TCS" in symbols


def test_single_stock_profile():
    res = client.get("/api/stocks/RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "RELIANCE"
    assert "quote" in data
    assert data["quote"]["current_price"] > 0


def test_stock_history():
    res = client.get("/api/stocks/RELIANCE/history?limit=50")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 50
    assert len(data["data"]) == 50
    candle = data["data"][0]
    for k in ["time", "open", "high", "low", "close", "volume"]:
        assert k in candle


def test_stock_indicators():
    res = client.get("/api/stocks/RELIANCE/indicators?limit=30")
    assert res.status_code == 200
    data = res.json()
    assert "active_signals" in data
    assert "indicator_catalog" in data
    assert len(data["history"]) == 30
    assert "rsi_14" in data["history"][-1]
    assert "macd" in data["history"][-1]


def test_stock_forecast():
    res = client.get("/api/stocks/RELIANCE/forecast")
    assert res.status_code == 200
    data = res.json()
    assert "horizons" in data
    assert "7_day" in data["horizons"]
    assert "14_day" in data["horizons"]
    assert "30_day" in data["horizons"]
    assert "walk_forward_validation" in data


def test_stock_risk():
    res = client.get("/api/stocks/RELIANCE/risk")
    assert res.status_code == 200
    data = res.json()
    assert "profile" in data
    assert "annualized_volatility" in data["profile"]
    assert "max_drawdown_pct" in data["profile"]
    assert "var_cvar" in data["profile"]


def test_portfolio_analysis():
    payload = {
        "weights": {"RELIANCE": 0.4, "TCS": 0.3, "HDFCBANK": 0.3},
        "risk_free_rate": 0.065
    }
    res = client.post("/api/portfolio/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "annualized_volatility" in data
    assert "expected_annual_return" in data
    assert "diversification_ratio" in data
    assert data["diversification_ratio"] >= 1.0


def test_models_performance():
    res = client.get("/api/models/performance")
    assert res.status_code == 200
    data = res.json()
    assert "leaderboard" in data
    assert "RELIANCE" in data["leaderboard"]


def test_ai_insights():
    res = client.get("/api/insights/RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "RELIANCE"
    assert "trend_summary" in data
    assert "volatility_observation" in data
    assert "risk_warning" in data
    assert "overall_stance" in data


def test_invalid_symbol_404():
    res = client.get("/api/stocks/INVALID_SYMBOL_XYZ")
    assert res.status_code == 404
