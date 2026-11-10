"""
Real-Time Streaming, Options Greeks & Sentiment Test Suite
"""
import os
import sys
import pytest
from starlette.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.main import app

client = TestClient(app)


def test_realtime_quotes():
    res = client.get("/api/realtime/quotes")
    assert res.status_code == 200
    data = res.json()
    assert "ticks" in data
    assert "RELIANCE" in data["ticks"]
    rel = data["ticks"]["RELIANCE"]
    assert "ltp" in rel
    assert "tick_direction" in rel
    assert rel["tick_direction"] in ["UP", "DOWN"]


def test_level2_market_depth():
    res = client.get("/api/realtime/depth/RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "RELIANCE"
    assert len(data["bids"]) == 5
    assert len(data["asks"]) == 5
    assert data["best_bid"] < data["best_ask"]
    assert "order_flow_imbalance" in data
    assert "buy_pressure_pct" in data


def test_intraday_candles():
    for tf in ["1M", "5M", "15M", "1H"]:
        res = client.get(f"/api/realtime/intraday/RELIANCE?timeframe={tf}&limit=30")
        assert res.status_code == 200
        data = res.json()
        assert data["timeframe"] == tf
        assert len(data["data"]) == 30
        c = data["data"][0]
        assert "open" in c and "close" in c and "high" in c and "low" in c


def test_options_chain_and_greeks():
    res = client.get("/api/options/chain/RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert "put_call_ratio" in data
    assert "max_pain_strike" in data
    assert "atm_greeks" in data
    assert "call_delta" in data["atm_greeks"]
    assert 0.0 <= data["atm_greeks"]["call_delta"] <= 1.0
    assert -1.0 <= data["atm_greeks"]["put_delta"] <= 0.0
    assert len(data["option_chain"]) > 0


def test_sentiment_news_wire():
    res = client.get("/api/sentiment/feed?symbol=RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert "feed" in data
    assert len(data["feed"]) > 0
    item = data["feed"][0]
    assert "headline" in item
    assert "sentiment" in item
    assert "score" in item
