"""
Phase 2 Test Suite: Data Preprocessing and Integrity Verification
"""
import os
import json
import pandas as pd
import numpy as np
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

TARGET_STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL"
]

TARGET_INDICES = [
    "NIFTY_50", "NIFTY_BANK", "NIFTY_IT", "NIFTY_NEXT_50", "INDIA_VIX"
]


def test_processed_files_exist():
    for sym in TARGET_STOCKS:
        parquet_path = os.path.join(PROCESSED_DIR, f"{sym}.parquet")
        csv_path = os.path.join(PROCESSED_DIR, f"{sym}.csv")
        assert os.path.exists(parquet_path), f"Processed parquet missing for stock {sym}"
        assert os.path.exists(csv_path), f"Processed csv missing for stock {sym}"

    for idx in TARGET_INDICES:
        parquet_path = os.path.join(PROCESSED_DIR, f"{idx}.parquet")
        assert os.path.exists(parquet_path), f"Processed parquet missing for index {idx}"


def test_schema_and_types():
    expected_cols = {
        "datetime", "open", "high", "low", "close", "volume",
        "symbol", "daily_return", "log_return", "cumulative_return", "datetime_str"
    }
    for sym in TARGET_STOCKS:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        assert expected_cols.issubset(set(df.columns)), f"Missing columns in {sym}: {expected_cols - set(df.columns)}"
        assert len(df) > 1000, f"Expected >1000 bars for {sym}, got {len(df)}"


def test_ohlc_geometric_integrity():
    for sym in TARGET_STOCKS:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        # High must be >= Open, High >= Close, High >= Low
        assert (df["high"] >= df["low"]).all(), f"High < Low in {sym}"
        assert (df["high"] >= df["open"] - 1e-5).all(), f"High < Open in {sym}"
        assert (df["high"] >= df["close"] - 1e-5).all(), f"High < Close in {sym}"
        assert (df["low"] <= df["open"] + 1e-5).all(), f"Low > Open in {sym}"
        assert (df["low"] <= df["close"] + 1e-5).all(), f"Low > Close in {sym}"
        assert (df["volume"] >= 0).all(), f"Negative volume in {sym}"


def test_chronological_ordering():
    for sym in TARGET_STOCKS:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        assert df["datetime"].is_monotonic_increasing, f"Dates not monotonic for {sym}"
        assert df["datetime"].duplicated().sum() == 0, f"Duplicates found in {sym}"


def test_financial_returns_consistency():
    for sym in TARGET_STOCKS:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        # Verify log returns are finite
        assert np.isfinite(df["log_return"]).all(), f"Non-finite log returns in {sym}"
        # Daily return should closely match (close[t] - close[t-1])/close[t-1]
        pct = (df["close"] / df["close"].shift(1) - 1.0).fillna(0.0)
        diff = np.abs(df["daily_return"] - pct)
        assert (diff < 1e-5).all(), f"Discrepancy in daily returns calculation for {sym}"


def test_data_quality_report():
    report_file = os.path.join(REPORTS_DIR, "data_quality_report.json")
    assert os.path.exists(report_file), "Data quality report missing"
    with open(report_file, "r") as f:
        data = json.load(f)
    assert len(data) >= 15, "Expected quality metrics for at least 15 instruments"
    for item in data.values():
        assert "cleaned_rows" in item
        assert "annualized_volatility" in item
        assert item["cleaned_rows"] > 1000
