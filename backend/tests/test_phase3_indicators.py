"""
Phase 3 Test Suite: Technical Indicators and Feature Extraction
"""
import os
import pandas as pd
import numpy as np
import pytest

from backend.features.technical_indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_atr, calculate_obv,
    generate_all_technical_features, generate_analytical_signals,
    indicator_catalog_metadata
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_DIR = os.path.join(BASE_DIR, "data", "features")


def test_rsi_bounds():
    prices = pd.Series([100, 102, 105, 103, 107, 110, 108, 112, 115, 114, 118, 122, 125, 123, 128, 130])
    rsi = calculate_rsi(prices, period=5)
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0.0).all() and (valid_rsi <= 100.0).all(), "RSI out of [0, 100] bounds"


def test_bollinger_bands_ordering():
    prices = pd.Series(np.linspace(100, 150, 50) + np.sin(np.linspace(0, 10, 50)) * 5)
    upper, mid, lower, bw, pct_b = calculate_bollinger_bands(prices, period=20, num_std=2.0)
    valid_idx = upper.dropna().index
    assert (upper.loc[valid_idx] >= mid.loc[valid_idx]).all(), "Upper band < Middle band"
    assert (mid.loc[valid_idx] >= lower.loc[valid_idx]).all(), "Middle band < Lower band"
    assert (bw.loc[valid_idx] >= 0.0).all(), "Bandwidth is negative"


def test_macd_relationship():
    prices = pd.Series(np.cumsum(np.random.normal(0, 1, 100)) + 100)
    macd, sig, hist = calculate_macd(prices, 12, 26, 9)
    valid_idx = hist.dropna().index
    diff = np.abs(hist.loc[valid_idx] - (macd.loc[valid_idx] - sig.loc[valid_idx]))
    assert (diff < 1e-8).all(), "MACD histogram != macd - signal"


def test_features_files_generated():
    target_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL"]
    for sym in target_stocks:
        parquet_path = os.path.join(FEATURES_DIR, f"{sym}_features.parquet")
        assert os.path.exists(parquet_path), f"Features parquet missing for {sym}"
        df = pd.read_parquet(parquet_path)
        assert "rsi_14" in df.columns
        assert "macd" in df.columns
        assert "bb_upper" in df.columns
        assert "atr_14" in df.columns
        assert "obv" in df.columns
        assert "sma_50" in df.columns
        assert "sma_200" in df.columns


def test_analytical_signals_structure():
    df = pd.read_parquet(os.path.join(FEATURES_DIR, "RELIANCE_features.parquet"))
    signals = generate_analytical_signals(df)
    assert len(signals) > 0, "No analytical signals generated"
    for s in signals:
        assert "indicator" in s
        assert "condition" in s
        assert "bias" in s
        assert "detail" in s
        assert s["bias"] in ["BULLISH_BIAS", "BEARISH_BIAS", "NEUTRAL"]


def test_indicator_catalog_metadata():
    catalog = indicator_catalog_metadata()
    required_indicators = ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands", "ATR", "OBV"]
    for req in required_indicators:
        assert req in catalog, f"Catalog missing {req}"
        assert "formula" in catalog[req]
        assert "interpretation" in catalog[req]
