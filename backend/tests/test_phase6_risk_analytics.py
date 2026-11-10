"""
Phase 6 Test Suite: Risk Intelligence and Portfolio Simulation
"""
import os
import json
import numpy as np
import pandas as pd
import pytest

from backend.risk.risk_engine import (
    calculate_historical_volatility, calculate_max_drawdown,
    calculate_var_and_cvar, calculate_sharpe_and_sortino,
    calculate_beta_and_alpha, simulate_portfolio_risk,
    risk_metrics_educational_metadata
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def test_volatility_calculation():
    # 1% daily std dev -> annualized is ~15.87%
    np.random.seed(42)
    daily_rets = pd.Series(np.random.normal(0.0005, 0.01, 1000))
    ann_vol = calculate_historical_volatility(daily_rets)
    assert 0.14 < ann_vol < 0.18, f"Unexpected annualized vol: {ann_vol}"


def test_max_drawdown():
    # Price path: 100 -> 120 -> 60 -> 90 -> min DD should be (120-60)/120 = 50%
    prices = pd.Series([100.0, 120.0, 90.0, 60.0, 80.0])
    mdd, peak_idx, trough_idx = calculate_max_drawdown(prices)
    assert np.isclose(mdd, 0.50), f"Expected 0.50, got {mdd}"
    assert peak_idx == "1"
    assert trough_idx == "3"


def test_cvar_greater_than_var():
    # Tail loss severity principle: CVaR >= VaR
    np.random.seed(42)
    rets = pd.Series(np.random.normal(0, 0.015, 1000))
    res = calculate_var_and_cvar(rets, [0.95, 0.99])
    for alpha_str in ["95%", "99%"]:
        h_var = res[alpha_str]["historical_var_1d"]
        h_cvar = res[alpha_str]["historical_cvar_1d"]
        assert h_cvar >= h_var, f"CVaR ({h_cvar}) < VaR ({h_var}) at {alpha_str}"


def test_benchmark_beta_identity():
    # Beta of an asset against itself must be 1.0, Alpha must be 0.0
    bench_df = pd.read_parquet(os.path.join(PROCESSED_DIR, "NIFTY_50.parquet"))
    ret = bench_df.set_index("datetime")["daily_return"]
    beta, alpha = calculate_beta_and_alpha(ret, ret)
    assert np.isclose(beta, 1.0, atol=0.01), f"Self-beta != 1.0, got {beta}"
    assert np.isclose(alpha, 0.0, atol=0.05), f"Self-alpha != 0.0, got {alpha}"


def test_portfolio_diversification_effect():
    # Combining RELIANCE and TCS should produce diversification ratio > 1.0
    res = simulate_portfolio_risk({"RELIANCE": 0.5, "TCS": 0.5})
    assert res["diversification_ratio"] >= 1.0, "Diversification ratio should be >= 1.0"
    assert "sharpe_ratio" in res
    assert "var_cvar" in res
    assert "portfolio_allocation" in res


def test_risk_reports_saved():
    risk_file = os.path.join(REPORTS_DIR, "risk_analytics.json")
    corr_file = os.path.join(REPORTS_DIR, "correlation_matrix.json")
    assert os.path.exists(risk_file), "Risk analytics report missing"
    assert os.path.exists(corr_file), "Correlation matrix report missing"

    with open(risk_file, "r") as f:
        profiles = json.load(f)
    assert "RELIANCE" in profiles
    assert "NIFTY_50" in profiles
    assert "max_drawdown_pct" in profiles["RELIANCE"]
    assert "rolling_drawdowns" in profiles["RELIANCE"]

    with open(corr_file, "r") as f:
        corr = json.load(f)
    assert len(corr["symbols"]) >= 10
    assert len(corr["matrix"]) >= 10


def test_risk_educational_metadata():
    meta = risk_metrics_educational_metadata()
    assert "Value at Risk (VaR)" in meta
    assert "limitations" in meta["Value at Risk (VaR)"]
    assert "Sharpe Ratio" in meta
