"""
MarketVision AI - AI Market Insights Engine
Synthesizes factual, data-grounded quantitative intelligence from real metrics and model predictions.
Operates deterministically without requiring a paid LLM API, with full architectural hooks
for plug-and-play LLM augmentation.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.preprocessing.data_pipeline import STOCKS_METADATA

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FEATURES_DIR = os.path.join(BASE_DIR, "data", "features")
PREDICTIONS_DIR = os.path.join(BASE_DIR, "data", "predictions")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")


def generate_asset_insights(symbol: str) -> Dict[str, Any]:
    """
    Synthesizes institutional market insights directly from computed quantitative metrics:
    1. Trend & Momentum Assessment
    2. Volatility & Tail Risk Warnings
    3. Volume Flow Observations
    4. Forecasting Uncertainty Interpretation
    5. Benchmark Alpha & Beta Positioning
    6. Optimal Model Selection Rationale
    """
    sym = symbol.upper().replace(".NS", "")
    meta = STOCKS_METADATA.get(sym, {"name": sym, "sector": "Indian Equities", "benchmark": "NIFTY 50"})

    # 1. Load Data
    feat_file = os.path.join(FEATURES_DIR, f"{sym}_features.parquet")
    risk_file = os.path.join(REPORTS_DIR, "risk_analytics.json")
    pred_file = os.path.join(PREDICTIONS_DIR, f"{sym}_forecast.json")
    lead_file = os.path.join(REPORTS_DIR, "model_leaderboard.json")

    df_feat = pd.read_parquet(feat_file) if os.path.exists(feat_file) else None
    with open(risk_file, "r") as f:
        risk_data = json.load(f).get(sym, {})
    with open(pred_file, "r") as f:
        pred_data = json.load(f) if os.path.exists(pred_file) else {}
    with open(lead_file, "r") as f:
        lead_data = json.load(f).get(sym, {})

    latest = df_feat.iloc[-1] if df_feat is not None else {}
    close_price = float(latest.get("close", 0.0))
    sma_50 = float(latest.get("sma_50", 0.0))
    sma_200 = float(latest.get("sma_200", 0.0))
    rsi = float(latest.get("rsi_14", 50.0))
    macd_hist = float(latest.get("macd_hist", 0.0))

    # Volume comparison
    curr_vol = float(latest.get("volume", 0.0))
    avg_vol_20 = float(df_feat["volume"].iloc[-20:].mean()) if df_feat is not None else curr_vol
    vol_ratio = (curr_vol / avg_vol_20) if avg_vol_20 > 0 else 1.0

    # Risk Metrics
    ann_vol = risk_data.get("annualized_volatility", 20.0)
    max_dd = risk_data.get("max_drawdown_pct", 0.0)
    var_95 = risk_data.get("var_cvar", {}).get("95%", {}).get("historical_var_1d", 2.0)
    cvar_95 = risk_data.get("var_cvar", {}).get("95%", {}).get("historical_cvar_1d", 3.0)
    beta = risk_data.get("beta_vs_nifty50", 1.0)
    alpha = risk_data.get("jensens_alpha_pct", 0.0)

    # Forecasts
    horizon_30 = pred_data.get("horizons", {}).get("30_day", {})
    exp_return_30d = horizon_30.get("expected_return_pct", 0.0)
    direction_30d = horizon_30.get("projected_direction", "NEUTRAL")
    best_model = lead_data.get("best_model", "ARIMA")
    rationale = lead_data.get("selection_rationale", "")

    # Structured Insights Synthesis
    trend_summary = (
        f"{meta['name']} is trading at ₹{close_price:,.2f}. The asset exhibits "
        f"{'a golden cross alignment with 50 SMA > 200 SMA' if sma_50 > sma_200 else 'a death cross alignment with 50 SMA < 200 SMA'}. "
        f"14-day RSI is currently at {rsi:.1f}, indicating a {'technically overbought' if rsi > 70 else ('technically oversold' if rsi < 30 else 'balanced neutral')} momentum regime. "
        f"MACD histogram reads {macd_hist:+.2f}, reflecting {'positive momentum expansion' if macd_hist > 0 else 'negative momentum pressure'}."
    )

    volatility_obs = (
        f"Historical annualized volatility is measured at {ann_vol:.1f}%. "
        f"The 95% 1-day Value at Risk (VaR) indicates a maximum expected single-day loss of {var_95:.2f}% under normal market distributions. "
        f"In extreme tail events, Conditional VaR (Expected Shortfall) increases the anticipated loss severity to {cvar_95:.2f}%."
    )

    volume_obs = (
        f"Trading volume stands at {curr_vol:,.0f} shares ({vol_ratio:.2f}x the 20-day moving average). "
        f"{'Unusually heavy institutional participation observed.' if vol_ratio > 1.5 else ('Subdued liquidity relative to recent baseline.' if vol_ratio < 0.7 else 'Volume remains in line with typical baseline participation.')}"
    )

    risk_warning = (
        f"Maximum historical drawdown was {max_dd:.1f}%. With a CAPM Beta of {beta:.2f} relative to NIFTY 50, "
        f"the stock exhibits {'higher sensitivity to broad market corrections' if beta > 1.1 else ('defensive low-beta characteristics' if beta < 0.9 else 'systematic market-aligned sensitivity')}. "
        f"Jensen's Alpha is {alpha:+.2f}% annualized."
    )

    forecast_explanation = (
        f"30-day quantitative trajectory projects a {direction_30d.lower()} bias with an expected price change of {exp_return_30d:+.2f}%. "
        f"Best validated model is {best_model}. {rationale} "
        f"Statistical uncertainty intervals widen over the forecast horizon, reflecting inherent macroeconomic drift."
    )

    return {
        "symbol": sym,
        "company_name": meta["name"],
        "sector": meta["sector"],
        "generated_at": str(df_feat["datetime_str"].iloc[-1]) if df_feat is not None else "Latest",
        "trend_summary": trend_summary,
        "volatility_observation": volatility_obs,
        "volume_observation": volume_obs,
        "risk_warning": risk_warning,
        "forecast_explanation": forecast_explanation,
        "overall_stance": "BULLISH_BIAS" if (rsi > 45 and sma_50 > sma_200 and exp_return_30d > 0) else ("BEARISH_BIAS" if (rsi < 45 and sma_50 < sma_200 and exp_return_30d < 0) else "NEUTRAL_CONSOLIDATION"),
        "confidence_level": "Moderate (Data-Grounded Quantitative Evidence)",
        "disclaimer": "AI insights are deterministically generated from quantitative indicators and time-series models for research and educational purposes. Not financial advice."
    }


if __name__ == "__main__":
    test_ins = generate_asset_insights("RELIANCE")
    print(json.dumps(test_ins, indent=2))
