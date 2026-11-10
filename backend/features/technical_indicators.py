"""
MarketVision AI - Quantitative Technical Indicators Engine
Implements institutional-grade technical indicators, signal generation, and feature extraction.
All signals generated are analytical research indicators, not investment advice.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FEATURES_DIR = os.path.join(BASE_DIR, "data", "features")


def calculate_sma(series: pd.Series, period: int = 20) -> pd.Series:
    """Simple Moving Average (SMA)."""
    return series.rolling(window=period, min_periods=period).mean()


def calculate_ema(series: pd.Series, period: int = 20) -> pd.Series:
    """Exponential Moving Average (EMA)."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI) using Wilder's exponential smoothing.
    Formula: 100 - (100 / (1 + RS)) where RS = Wilder Smoothed Gain / Wilder Smoothed Loss
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Wilder's smoothing: alpha = 1 / period
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    # Handle zero loss case
    rsi = rsi.fillna(100.0).where(avg_loss != 0, 100.0)
    # If both gain and loss are 0, RSI is 50
    rsi = rsi.where((avg_gain != 0) | (avg_loss != 0), 50.0)
    return rsi


def calculate_macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Moving Average Convergence Divergence (MACD).
    Returns (macd_line, signal_line, histogram).
    """
    ema_fast = calculate_ema(series, fast_period)
    ema_slow = calculate_ema(series, slow_period)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    series: pd.Series,
    period: int = 20,
    num_std: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands.
    Returns (upper_band, middle_band, lower_band, bandwidth, percent_b).
    """
    middle_band = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    # Bandwidth = (Upper - Lower) / Middle
    bandwidth = (upper_band - lower_band) / middle_band.replace(0, np.nan)
    # %B = (Close - Lower) / (Upper - Lower)
    band_range = (upper_band - lower_band).replace(0, np.nan)
    percent_b = (series - lower_band) / band_range
    return upper_band, middle_band, lower_band, bandwidth, percent_b


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range (ATR).
    True Range = max(High - Low, abs(High - Close_prev), abs(Low - Close_prev))
    """
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Wilder's smoothing for ATR
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def calculate_obv(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    On-Balance Volume (OBV) and OBV 20-period EMA.
    """
    close = df["close"]
    volume = df["volume"]
    direction = np.sign(close.diff()).fillna(0)
    obv = (direction * volume).cumsum()
    obv_ema = calculate_ema(obv, 20)
    return obv, obv_ema


def generate_all_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates all technical indicators and appends them as features to the DataFrame.
    """
    df_feat = df.copy()

    # Simple Moving Averages
    df_feat["sma_20"] = calculate_sma(df_feat["close"], 20)
    df_feat["sma_50"] = calculate_sma(df_feat["close"], 50)
    df_feat["sma_200"] = calculate_sma(df_feat["close"], 200)

    # Exponential Moving Averages
    df_feat["ema_9"] = calculate_ema(df_feat["close"], 9)
    df_feat["ema_21"] = calculate_ema(df_feat["close"], 21)
    df_feat["ema_50"] = calculate_ema(df_feat["close"], 50)
    df_feat["ema_200"] = calculate_ema(df_feat["close"], 200)

    # Relative Strength Index
    df_feat["rsi_14"] = calculate_rsi(df_feat["close"], 14)

    # MACD
    macd, signal, hist = calculate_macd(df_feat["close"], 12, 26, 9)
    df_feat["macd"] = macd
    df_feat["macd_signal"] = signal
    df_feat["macd_hist"] = hist

    # Bollinger Bands
    upper, mid, lower, bw, pct_b = calculate_bollinger_bands(df_feat["close"], 20, 2.0)
    df_feat["bb_upper"] = upper
    df_feat["bb_middle"] = mid
    df_feat["bb_lower"] = lower
    df_feat["bb_bandwidth"] = bw
    df_feat["bb_percent_b"] = pct_b

    # ATR
    df_feat["atr_14"] = calculate_atr(df_feat, 14)

    # OBV
    obv, obv_ema = calculate_obv(df_feat)
    df_feat["obv"] = obv
    df_feat["obv_ema"] = obv_ema

    # Rolling Volatility (21-day annualized)
    df_feat["volatility_21d"] = df_feat["daily_return"].rolling(21).std() * np.sqrt(252)

    return df_feat


def generate_analytical_signals(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Evaluates latest market data and produces technical analytical signals.
    Note: These are purely technical condition flags for research and screening.
    """
    if len(df) < 200:
        return []

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    signals = []

    # 1. RSI Signals
    rsi = latest.get("rsi_14")
    if pd.notna(rsi):
        if rsi < 30:
            signals.append({
                "indicator": "RSI (14)",
                "condition": "Oversold Condition",
                "bias": "BULLISH_BIAS",
                "value": round(float(rsi), 2),
                "detail": f"RSI is at {rsi:.2f} (< 30.0 threshold), indicating technical oversold territory."
            })
        elif rsi > 70:
            signals.append({
                "indicator": "RSI (14)",
                "condition": "Overbought Condition",
                "bias": "BEARISH_BIAS",
                "value": round(float(rsi), 2),
                "detail": f"RSI is at {rsi:.2f} (> 70.0 threshold), indicating technical overbought territory."
            })
        else:
            signals.append({
                "indicator": "RSI (14)",
                "condition": "Neutral Range",
                "bias": "NEUTRAL",
                "value": round(float(rsi), 2),
                "detail": f"RSI is balanced at {rsi:.2f} within standard 30-70 corridor."
            })

    # 2. MACD Crossover
    macd_curr = latest.get("macd")
    sig_curr = latest.get("macd_signal")
    macd_prev = prev.get("macd")
    sig_prev = prev.get("macd_signal")

    if pd.notna(macd_curr) and pd.notna(sig_curr) and pd.notna(macd_prev) and pd.notna(sig_prev):
        if macd_prev <= sig_prev and macd_curr > sig_curr:
            signals.append({
                "indicator": "MACD (12, 26, 9)",
                "condition": "Bullish Signal Crossover",
                "bias": "BULLISH_BIAS",
                "value": round(float(macd_curr - sig_curr), 2),
                "detail": "MACD line crossed above the 9-day signal line, indicating positive momentum expansion."
            })
        elif macd_prev >= sig_prev and macd_curr < sig_curr:
            signals.append({
                "indicator": "MACD (12, 26, 9)",
                "condition": "Bearish Signal Crossover",
                "bias": "BEARISH_BIAS",
                "value": round(float(macd_curr - sig_curr), 2),
                "detail": "MACD line crossed below the 9-day signal line, indicating negative momentum expansion."
            })
        else:
            trend = "Bullish" if macd_curr > sig_curr else "Bearish"
            signals.append({
                "indicator": "MACD (12, 26, 9)",
                "condition": f"{trend} Momentum State",
                "bias": "BULLISH_BIAS" if trend == "Bullish" else "BEARISH_BIAS",
                "value": round(float(latest.get("macd_hist", 0)), 2),
                "detail": f"MACD histogram is at {latest.get('macd_hist', 0):.2f} with MACD {'above' if trend=='Bullish' else 'below'} signal line."
            })

    # 3. Moving Average Golden / Death Cross
    sma_50 = latest.get("sma_50")
    sma_200 = latest.get("sma_200")
    close = latest.get("close")
    if pd.notna(sma_50) and pd.notna(sma_200):
        if sma_50 > sma_200:
            signals.append({
                "indicator": "Moving Average Alignment",
                "condition": "Golden Cross Alignment",
                "bias": "BULLISH_BIAS",
                "value": round(float(sma_50 - sma_200), 2),
                "detail": f"50-day SMA ({sma_50:.2f}) trades above 200-day SMA ({sma_200:.2f}), confirming medium-term uptrend structure."
            })
        else:
            signals.append({
                "indicator": "Moving Average Alignment",
                "condition": "Death Cross Alignment",
                "bias": "BEARISH_BIAS",
                "value": round(float(sma_50 - sma_200), 2),
                "detail": f"50-day SMA ({sma_50:.2f}) trades below 200-day SMA ({sma_200:.2f}), reflecting long-term macro weakness."
            })

    # 4. Bollinger Bands Status
    pct_b = latest.get("bb_percent_b")
    bw = latest.get("bb_bandwidth")
    if pd.notna(pct_b) and pd.notna(bw):
        if pct_b > 1.0:
            signals.append({
                "indicator": "Bollinger Bands (20, 2)",
                "condition": "Upper Band Breakout",
                "bias": "BULLISH_BIAS",
                "value": round(float(pct_b), 2),
                "detail": f"Price is trading above the upper Bollinger Band (%B: {pct_b:.2f}), indicating elevated upward volatility."
            })
        elif pct_b < 0.0:
            signals.append({
                "indicator": "Bollinger Bands (20, 2)",
                "condition": "Lower Band Penetration",
                "bias": "BEARISH_BIAS",
                "value": round(float(pct_b), 2),
                "detail": f"Price is trading below the lower Bollinger Band (%B: {pct_b:.2f}), indicating severe downward extension."
            })
        else:
            signals.append({
                "indicator": "Bollinger Bands (20, 2)",
                "condition": "Within Normal Envelope",
                "bias": "NEUTRAL",
                "value": round(float(pct_b), 2),
                "detail": f"Price is contained within the standard 2-sigma envelope (%B: {pct_b:.2f}, Bandwidth: {bw:.3f})."
            })

    return signals


def indicator_catalog_metadata() -> Dict[str, Dict[str, str]]:
    """Educational metadata and theoretical explanations for each indicator."""
    return {
        "SMA": {
            "name": "Simple Moving Average",
            "formula": "SMA_t = (1/n) * sum(P_{t-i}) for i=0 to n-1",
            "interpretation": "Smooths out price fluctuations to identify directional trend. Commonly used periods are 20 (short-term), 50 (intermediate), and 200 (institutional long-term trend benchmark).",
            "signals": "Golden cross (50 SMA crossing above 200 SMA) indicates long-term bullish transition; Death cross indicates long-term bearish transition."
        },
        "EMA": {
            "name": "Exponential Moving Average",
            "formula": "EMA_t = alpha * P_t + (1 - alpha) * EMA_{t-1}, where alpha = 2 / (n + 1)",
            "interpretation": "Applies weighting factors that decrease exponentially, reacting faster to recent price fluctuations than an SMA.",
            "signals": "Short EMA (9) crossing medium EMA (21) provides rapid trend acceleration insights."
        },
        "RSI": {
            "name": "Relative Strength Index",
            "formula": "RSI = 100 - (100 / (1 + (Smoothed Gain / Smoothed Loss)))",
            "interpretation": "Oscillator measuring speed and change of price movements between 0 and 100 with Wilder smoothing.",
            "signals": "Values below 30 denote oversold conditions; values above 70 denote overbought conditions; divergence with price marks potential reversals."
        },
        "MACD": {
            "name": "Moving Average Convergence Divergence",
            "formula": "MACD Line = EMA(12) - EMA(26); Signal Line = EMA(9, MACD Line); Histogram = MACD Line - Signal Line",
            "interpretation": "Trend-following momentum indicator displaying the relationship between two moving averages of an asset's price.",
            "signals": "Bullish centerline or signal crossovers indicate rising upside momentum; bearish crossovers indicate deteriorating momentum."
        },
        "Bollinger Bands": {
            "name": "Bollinger Bands",
            "formula": "Middle = SMA(20); Upper = Middle + (2 * sigma); Lower = Middle - (2 * sigma)",
            "interpretation": "Volatility bands placed above and below a central moving average, expanding during volatile periods and contracting during consolidations.",
            "signals": "Price touching bands denotes extreme statistical deviation; band contraction (squeeze) frequently precedes high-volatility expansions."
        },
        "ATR": {
            "name": "Average True Range",
            "formula": "ATR_t = (ATR_{t-1} * (n - 1) + TR_t) / n",
            "interpretation": "Measures market volatility by decomposing the entire range of an asset for that period including inter-bar gaps.",
            "signals": "High ATR values denote elevated market volatility; low ATR values denote low-volatility compression."
        },
        "OBV": {
            "name": "On-Balance Volume",
            "formula": "OBV_t = OBV_{t-1} + (Volume_t if Close_t > Close_{t-1} else -Volume_t)",
            "interpretation": "Cumulative volume indicator relating volume flow to price direction, assessing institutional accumulation or distribution.",
            "signals": "Rising OBV indicates accumulation; falling OBV confirms distribution; divergence against price warns of trend exhaustion."
        }
    }


def process_and_save_all_features():
    """
    Computes and saves technical indicator features for all processed stocks and indices.
    """
    os.makedirs(FEATURES_DIR, exist_ok=True)
    all_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith(".parquet")]

    summary = {}
    for filename in all_files:
        symbol_key = filename.replace(".parquet", "")
        df_processed = pd.read_parquet(os.path.join(PROCESSED_DIR, filename))

        df_features = generate_all_technical_features(df_processed)
        dest_parquet = os.path.join(FEATURES_DIR, f"{symbol_key}_features.parquet")
        dest_csv = os.path.join(FEATURES_DIR, f"{symbol_key}_features.csv")

        df_features.to_parquet(dest_parquet, index=False)
        df_features.to_csv(dest_csv, index=False)

        signals = generate_analytical_signals(df_features)
        summary[symbol_key] = {
            "feature_count": len(df_features.columns),
            "rows": len(df_features),
            "latest_close": float(df_features["close"].iloc[-1]),
            "latest_rsi": float(df_features["rsi_14"].iloc[-1]) if pd.notna(df_features["rsi_14"].iloc[-1]) else None,
            "active_signals_count": len(signals)
        }
        logger.info(f"Generated {len(df_features.columns)} features for {symbol_key}")

    return summary


if __name__ == "__main__":
    summary = process_and_save_all_features()
    print("Features extraction completed successfully for", len(summary), "instruments.")
