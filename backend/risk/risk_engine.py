"""
MarketVision AI - Quantitative Risk Intelligence Engine
Implements institutional risk metrics: Historical & Rolling Volatility,
Maximum Drawdown, Historical & Parametric VaR, CVaR (Expected Shortfall),
Sharpe Ratio, Sortino Ratio, Beta vs NIFTY 50, Correlation Matrices,
and Multi-Asset Portfolio Risk Simulation.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Tuple, Any

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

# Annualized Indian Risk-Free Rate (RBI 10-Year Government Bond Yield benchmark)
RISK_FREE_RATE = 0.065
TRADING_DAYS_PER_YEAR = 252


def calculate_historical_volatility(returns: pd.Series) -> float:
    """Annualized standard deviation of daily returns."""
    clean_ret = returns.dropna()
    if len(clean_ret) < 2:
        return 0.0
    return float(clean_ret.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, Optional[str], Optional[str]]:
    """
    Computes Maximum Drawdown (MDD) and peak/trough index dates.
    Drawdown = (Price_t - Peak_t) / Peak_t.
    """
    cum_max = prices.cummax()
    drawdowns = (prices - cum_max) / cum_max
    min_dd = float(drawdowns.min())
    
    trough_idx = drawdowns.idxmin()
    peak_idx = prices.loc[:trough_idx].idxmax() if pd.notna(trough_idx) else None

    return abs(min_dd), str(peak_idx), str(trough_idx)


def calculate_var_and_cvar(
    returns: pd.Series,
    confidence_levels: List[float] = [0.95, 0.99]
) -> Dict[str, Dict[str, float]]:
    """
    Computes Value at Risk (VaR) and Conditional Value at Risk (CVaR / Expected Shortfall)
    using both Historical Simulation and Parametric Cornish-Fisher expansions.
    Expressed as positive percentages representing maximum projected loss.
    """
    clean_ret = returns.dropna().values
    if len(clean_ret) < 30:
        return {}

    mu = float(np.mean(clean_ret))
    sigma = float(np.std(clean_ret))
    skew = float(stats.skew(clean_ret))
    kurt = float(stats.kurtosis(clean_ret))  # excess kurtosis

    results = {}
    for alpha in confidence_levels:
        # 1. Historical VaR: Empirical quantile of returns
        cutoff = (1.0 - alpha) * 100.0
        hist_var = -float(np.percentile(clean_ret, cutoff))
        
        # Historical CVaR: Mean of returns exceeding VaR loss threshold
        tail_losses = clean_ret[clean_ret <= -hist_var]
        hist_cvar = -float(np.mean(tail_losses)) if len(tail_losses) > 0 else hist_var

        # 2. Parametric Gaussian VaR
        z = stats.norm.ppf(alpha)
        param_var = float(z * sigma - mu)

        # 3. Cornish-Fisher VaR (Adjusted for skewness & fat-tail kurtosis)
        # z_cf = z + (z^2 - 1)*S/6 + (z^3 - 3z)*K/24 - (2z^3 - 5z)*S^2/36
        z_cf = (
            z
            + ((z**2 - 1.0) * skew / 6.0)
            + ((z**3 - 3.0 * z) * kurt / 24.0)
            - ((2.0 * z**3 - 5.0 * z) * (skew**2) / 36.0)
        )
        cf_var = float(z_cf * sigma - mu)

        results[f"{int(alpha * 100)}%"] = {
            "historical_var_1d": round(max(0.0, hist_var) * 100.0, 2),
            "historical_cvar_1d": round(max(0.0, hist_cvar) * 100.0, 2),
            "parametric_var_1d": round(max(0.0, param_var) * 100.0, 2),
            "cornish_fisher_var_1d": round(max(0.0, cf_var) * 100.0, 2),
            "historical_var_10d": round(max(0.0, hist_var * np.sqrt(10.0)) * 100.0, 2),
        }

    return results


def calculate_sharpe_and_sortino(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> Tuple[float, float]:
    """
    Computes annualized Sharpe Ratio and Sortino Ratio.
    Daily Rf = (1 + Rf)^(1/252) - 1.
    Downside deviation penalizes only returns below target/Rf.
    """
    clean_ret = returns.dropna()
    if len(clean_ret) < 2:
        return 0.0, 0.0

    daily_rf = (1.0 + risk_free_rate) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0
    excess_ret = clean_ret - daily_rf

    mean_excess = excess_ret.mean()
    ann_excess = mean_excess * TRADING_DAYS_PER_YEAR
    ann_std = clean_ret.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    sharpe = float(ann_excess / ann_std) if ann_std > 0 else 0.0

    # Downside deviation: sqrt(E[min(0, r - rf)^2])
    downside_ret = excess_ret.clip(upper=0.0)
    ann_downside_std = float(np.sqrt(np.mean(downside_ret**2)) * np.sqrt(TRADING_DAYS_PER_YEAR))

    sortino = float(ann_excess / ann_downside_std) if ann_downside_std > 0 else 0.0
    return round(sharpe, 2), round(sortino, 2)


def calculate_beta_and_alpha(asset_returns: pd.Series, benchmark_returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> Tuple[float, float]:
    """
    Computes Capital Asset Pricing Model (CAPM) Beta and Jensen's Alpha against NIFTY 50.
    Beta = Cov(Ri, Rm) / Var(Rm).
    """
    aligned = pd.concat([asset_returns, benchmark_returns], axis=1, sort=False).dropna()
    if len(aligned) < 30:
        return 1.0, 0.0

    r_i = aligned.iloc[:, 0].values
    r_m = aligned.iloc[:, 1].values

    var_m = np.var(r_m, ddof=1)
    if var_m == 0:
        return 1.0, 0.0

    cov_im = np.cov(r_i, r_m)[0, 1]
    beta = float(cov_im / var_m)

    # Annualized Jensen's Alpha: Alpha = R_i - [Rf + Beta * (R_m - Rf)]
    ann_ri = float(np.mean(r_i) * TRADING_DAYS_PER_YEAR)
    ann_rm = float(np.mean(r_m) * TRADING_DAYS_PER_YEAR)
    alpha = float(ann_ri - (risk_free_rate + beta * (ann_rm - risk_free_rate)))

    return round(beta, 2), round(alpha * 100.0, 2)


def generate_single_stock_risk_profile(symbol: str, benchmark_df: pd.DataFrame) -> Dict[str, Any]:
    """Generates complete risk profile for a single stock."""
    file_path = os.path.join(PROCESSED_DIR, f"{symbol}.parquet")
    df = pd.read_parquet(file_path).set_index("datetime")
    bench = benchmark_df.set_index("datetime")

    ret = df["daily_return"]
    bench_ret = bench["daily_return"]

    hist_vol = calculate_historical_volatility(ret)
    rolling_vol_21 = float(ret.rolling(21).std().iloc[-1] * np.sqrt(TRADING_DAYS_PER_YEAR))
    rolling_vol_63 = float(ret.rolling(63).std().iloc[-1] * np.sqrt(TRADING_DAYS_PER_YEAR))

    mdd, peak_d, trough_d = calculate_max_drawdown(df["close"])
    var_cvar = calculate_var_and_cvar(ret)
    sharpe, sortino = calculate_sharpe_and_sortino(ret)
    beta, alpha = calculate_beta_and_alpha(ret, bench_ret)

    # 1-year annualized return
    recent_ret = ret.iloc[-252:] if len(ret) >= 252 else ret
    ann_return_1y = float(recent_ret.mean() * TRADING_DAYS_PER_YEAR)

    # Rolling Drawdown Series (last 60 trading days) for interactive visualization
    cum_max_60 = df["close"].iloc[-60:].cummax()
    dd_series = ((df["close"].iloc[-60:] - cum_max_60) / cum_max_60 * 100.0).round(2)
    rolling_dd_list = [
        {"date": str(d.date()), "drawdown_pct": float(val)}
        for d, val in dd_series.items()
    ]

    return {
        "symbol": symbol,
        "annualized_volatility": round(hist_vol * 100.0, 2),
        "rolling_volatility_21d": round(rolling_vol_21 * 100.0, 2),
        "rolling_volatility_63d": round(rolling_vol_63 * 100.0, 2),
        "annualized_return_1y": round(ann_return_1y * 100.0, 2),
        "max_drawdown_pct": round(mdd * 100.0, 2),
        "drawdown_peak_date": peak_d[:10] if peak_d else None,
        "drawdown_trough_date": trough_d[:10] if trough_d else None,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "beta_vs_nifty50": beta,
        "jensens_alpha_pct": alpha,
        "risk_free_rate_used": round(RISK_FREE_RATE * 100.0, 2),
        "var_cvar": var_cvar,
        "rolling_drawdowns": rolling_dd_list
    }


def compute_cross_asset_correlation() -> Dict[str, Any]:
    """Calculates correlation and covariance matrix across all 10 stocks and NIFTY 50."""
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL", "NIFTY_50"]

    returns_dict = {}
    for sym in symbols:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        returns_dict[sym] = df.set_index("datetime")["daily_return"]

    combined_returns = pd.DataFrame(returns_dict).dropna()
    corr_matrix = combined_returns.corr().round(3)
    cov_matrix = (combined_returns.cov() * TRADING_DAYS_PER_YEAR).round(6)

    # Format for heatmap JSON
    corr_formatted = []
    for s1 in symbols:
        row_dict = {"symbol": s1}
        for s2 in symbols:
            row_dict[s2] = float(corr_matrix.loc[s1, s2])
        corr_formatted.append(row_dict)

    return {
        "symbols": symbols,
        "matrix": corr_formatted,
        "covariance": cov_matrix.to_dict()
    }


def simulate_portfolio_risk(
    weights: Dict[str, float],
    risk_free_rate: float = RISK_FREE_RATE
) -> Dict[str, Any]:
    """
    Simulates multi-asset portfolio metrics given user-defined weights.
    Returns expected return, volatility, Sharpe, Sortino, VaR, CVaR, and Diversification Ratio.
    """
    symbols = list(weights.keys())
    w = np.array([weights[s] for s in symbols], dtype=float)
    
    # Normalize weights to sum to 1.0
    if np.sum(w) > 0:
        w = w / np.sum(w)
    else:
        w = np.ones(len(symbols)) / len(symbols)

    returns_dict = {}
    for sym in symbols:
        df = pd.read_parquet(os.path.join(PROCESSED_DIR, f"{sym}.parquet"))
        returns_dict[sym] = df.set_index("datetime")["daily_return"]

    combined_returns = pd.DataFrame(returns_dict).dropna()
    
    # Portfolio Daily Returns Series
    port_daily_ret = combined_returns.dot(w)

    # Annualized Return and Volatility
    exp_ann_ret = float(np.mean(port_daily_ret) * TRADING_DAYS_PER_YEAR)
    ann_cov = combined_returns.cov().values * TRADING_DAYS_PER_YEAR
    port_variance = float(np.dot(w.T, np.dot(ann_cov, w)))
    port_vol = float(np.sqrt(max(0.0, port_variance)))

    # Weighted individual volatilities
    indiv_vols = combined_returns.std().values * np.sqrt(TRADING_DAYS_PER_YEAR)
    weighted_vol = float(np.sum(w * indiv_vols))
    diversification_ratio = round(weighted_vol / port_vol, 2) if port_vol > 0 else 1.0

    # Max Drawdown
    cum_wealth = (1.0 + port_daily_ret).cumprod()
    mdd, _, _ = calculate_max_drawdown(cum_wealth)

    # Sharpe & Sortino
    sharpe, sortino = calculate_sharpe_and_sortino(port_daily_ret, risk_free_rate)

    # VaR and CVaR
    var_cvar = calculate_var_and_cvar(port_daily_ret)

    # Normalized weights dict
    normalized_weights = {s: round(float(w[i]) * 100.0, 1) for i, s in enumerate(symbols)}

    return {
        "portfolio_allocation": normalized_weights,
        "expected_annual_return": round(exp_ann_ret * 100.0, 2),
        "annualized_volatility": round(port_vol * 100.0, 2),
        "diversification_ratio": diversification_ratio,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown_pct": round(mdd * 100.0, 2),
        "var_cvar": var_cvar,
        "risk_tier": "Low" if port_vol < 0.15 else ("Moderate" if port_vol < 0.25 else "High")
    }


def risk_metrics_educational_metadata() -> Dict[str, Dict[str, str]]:
    """Educational metadata and financial limitations for each metric."""
    return {
        "Historical Volatility": {
            "definition": "Annualized standard deviation of asset daily returns (sigma * sqrt(252)).",
            "interpretation": "Represents the total dispersion of price swings around historical mean return.",
            "limitations": "Treats upside and downside volatility symmetrically, assuming returns follow a stationary distribution."
        },
        "Maximum Drawdown": {
            "definition": "Peak-to-trough decline before a new peak is achieved: (Trough - Peak) / Peak.",
            "interpretation": "Measures worst-case historical capital erosion and historical pain threshold.",
            "limitations": "Path-dependent metric based on past price history; does not bound future potential catastrophic events."
        },
        "Value at Risk (VaR)": {
            "definition": "Maximum estimated monetary or percentage loss over a specified horizon at a given confidence level (e.g. 95% 1-day).",
            "interpretation": "Answers: 'How much can I lose on an ordinary bad day with 95% confidence?'",
            "limitations": "Sub-additive violation: Not a coherent risk measure; remains completely blind to the magnitude of losses beyond the alpha percentile cut-off."
        },
        "Conditional VaR (CVaR / Expected Shortfall)": {
            "definition": "Expected value of losses given that the loss exceeds the VaR threshold.",
            "interpretation": "Answers: 'If catastrophe occurs and we breach the 95% threshold, what is the average severity of the loss?'",
            "limitations": "Coherent risk measure, but sensitive to extreme outlier estimation in finite historical samples."
        },
        "Sharpe Ratio": {
            "definition": "(Mean Portfolio Return - Risk-Free Rate) / Annualized Volatility.",
            "interpretation": "Quantifies excess return generated per unit of total risk.",
            "limitations": "Penalizes desirable upside volatility identically to destructive downside drawdowns."
        },
        "Sortino Ratio": {
            "definition": "(Mean Portfolio Return - Risk-Free Rate) / Downside Semi-Deviation.",
            "interpretation": "Isolates harmful downside volatility, providing a more refined view of risk-adjusted performance.",
            "limitations": "Dependent on the chosen minimum acceptable return (MAR) and requires sufficient negative return data points."
        },
        "Beta": {
            "definition": "Covariance of asset returns with benchmark NIFTY 50 divided by benchmark variance.",
            "interpretation": "Quantifies systematic market risk sensitivity. Beta > 1 denotes aggressive amplification; Beta < 1 denotes defensive buffering.",
            "limitations": "Assumes a linear, static relationship; fails during severe market contagion when correlations break toward 1."
        }
    }


def generate_and_save_all_risk_intelligence():
    """Generates and saves risk profiles, correlation matrices, and sample portfolios."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    bench_df = pd.read_parquet(os.path.join(PROCESSED_DIR, "NIFTY_50.parquet"))

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL"]

    # 1. Single-stock risk profiles
    risk_profiles = {}
    for sym in symbols:
        logger.info(f"Computing risk profile for {sym}...")
        risk_profiles[sym] = generate_single_stock_risk_profile(sym, bench_df)

    risk_profiles["NIFTY_50"] = generate_single_stock_risk_profile("NIFTY_50", bench_df)

    # 2. Cross-asset correlation
    logger.info("Computing cross-asset correlation matrix...")
    corr_data = compute_cross_asset_correlation()

    # 3. Sample Institutional Balanced Portfolio Simulation
    sample_portfolio = simulate_portfolio_risk({
        "RELIANCE": 0.20,
        "TCS": 0.15,
        "HDFCBANK": 0.20,
        "INFY": 0.15,
        "ITC": 0.15,
        "BHARTIARTL": 0.15
    })

    # Save to disk
    with open(os.path.join(REPORTS_DIR, "risk_analytics.json"), "w", encoding="utf-8") as f:
        json.dump(risk_profiles, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "correlation_matrix.json"), "w", encoding="utf-8") as f:
        json.dump(corr_data, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "sample_portfolio_risk.json"), "w", encoding="utf-8") as f:
        json.dump(sample_portfolio, f, indent=2)

    logger.info("Risk intelligence generation complete!")
    return risk_profiles, corr_data, sample_portfolio


if __name__ == "__main__":
    generate_and_save_all_risk_intelligence()
