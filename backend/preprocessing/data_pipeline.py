"""
MarketVision AI - Data Ingestion and Preprocessing Pipeline
Handles acquisition, validation, cleansing, and normalization of NSE stock and index data.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
RAW_STOCKS_DIR = os.path.join(RAW_DIR, "stocks")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

# Target Stocks Metadata
STOCKS_METADATA = {
    "RELIANCE": {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd.", "sector": "Energy & Conglomerate", "benchmark": "NIFTY 50"},
    "TCS": {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd.", "sector": "Information Technology", "benchmark": "CNXIT"},
    "INFY": {"ticker": "INFY.NS", "name": "Infosys Ltd.", "sector": "Information Technology", "benchmark": "CNXIT"},
    "HDFCBANK": {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd.", "sector": "Banking & Financials", "benchmark": "NIFTYPVTBANK"},
    "ICICIBANK": {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd.", "sector": "Banking & Financials", "benchmark": "NIFTYPVTBANK"},
    "SBIN": {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking & Financials", "benchmark": "CNXPSUBANK"},
    "ITC": {"ticker": "ITC.NS", "name": "ITC Ltd.", "sector": "FMCG", "benchmark": "CNXFMCG"},
    "LT": {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd.", "sector": "Infrastructure & Capital Goods", "benchmark": "NIFTY 50"},
    "AXISBANK": {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd.", "sector": "Banking & Financials", "benchmark": "NIFTYPVTBANK"},
    "BHARTIARTL": {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd.", "sector": "Telecommunications", "benchmark": "NIFTY 50"},
}

# Key Index Mappings from raw indices CSV
INDICES_METADATA = {
    "NIFTY 50": {"raw_symbol": "NIFTY", "name": "NIFTY 50 Index", "sector": "Broad Market Benchmark"},
    "NIFTY BANK": {"raw_symbol": "NIFTYPVTBANK", "name": "NIFTY Private Bank Index", "sector": "Banking Benchmark"},
    "NIFTY IT": {"raw_symbol": "CNXIT", "name": "NIFTY IT Index", "sector": "IT Benchmark"},
    "NIFTY NEXT 50": {"raw_symbol": "NIFTYJR", "name": "NIFTY Next 50 Index", "sector": "Large Cap Junior"},
    "INDIA VIX": {"raw_symbol": "INDIAVIX", "name": "India Volatility Index", "sector": "Volatility Benchmark"}
}


def download_raw_stock_data(start_date: str = "2018-01-01", end_date: str = "2024-12-31") -> Dict[str, str]:
    """
    Downloads historical daily OHLCV data for the 10 target NSE stocks via yfinance.
    Saves unmodified raw CSVs into backend/data/raw/stocks/.
    """
    import yfinance as yf

    os.makedirs(RAW_STOCKS_DIR, exist_ok=True)
    saved_files = {}

    for symbol, meta in STOCKS_METADATA.items():
        ticker = meta["ticker"]
        dest_path = os.path.join(RAW_STOCKS_DIR, f"{symbol}_raw.csv")
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
            logger.info(f"Raw data for {symbol} already exists at {dest_path}, skipping download.")
            saved_files[symbol] = dest_path
            continue

        logger.info(f"Downloading raw data for {symbol} ({ticker})...")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                continue

            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            df.reset_index(inplace=True)
            df.to_csv(dest_path, index=False)
            saved_files[symbol] = dest_path
            logger.info(f"Saved {symbol} raw data ({len(df)} rows) to {dest_path}")
        except Exception as e:
            logger.error(f"Failed to download raw data for {symbol}: {e}")

    return saved_files


def clean_and_normalize_ohlcv(
    df: pd.DataFrame,
    symbol: str,
    datetime_col: str = "Date",
    open_col: str = "Open",
    high_col: str = "High",
    low_col: str = "Low",
    close_col: str = "Close",
    volume_col: str = "Volume"
) -> Tuple[pd.DataFrame, Dict]:
    """
    Standardizes, validates, and cleans an OHLCV dataset.
    Returns the cleaned DataFrame and a dictionary of data quality metrics.
    """
    initial_rows = len(df)
    
    # 1. Rename columns to standard lowercase
    target_mappings = {
        "datetime": ["datetime", "date", "timestamp", datetime_col.lower()],
        "open": ["open", open_col.lower()],
        "high": ["high", high_col.lower()],
        "low": ["low", low_col.lower()],
        "close": ["close", close_col.lower()],
        "volume": ["volume", "vol", volume_col.lower()]
    }

    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    resolved_col_map = {}
    for standard_col, candidates in target_mappings.items():
        for cand in candidates:
            if cand in cols_lower:
                resolved_col_map[cols_lower[cand]] = standard_col
                break

    df_cleaned = df.rename(columns=resolved_col_map).copy()
    
    # Ensure required columns exist
    required_cols = ["datetime", "open", "high", "low", "close", "volume"]
    for col in required_cols:
        if col not in df_cleaned.columns:
            if col == "volume":
                df_cleaned["volume"] = 0.0
            else:
                raise ValueError(f"Required column '{col}' missing from data for {symbol}")

    # Keep only relevant columns + symbol
    df_cleaned = df_cleaned[required_cols].copy()
    df_cleaned["symbol"] = symbol

    # 2. Date conversion and chronological sorting
    df_cleaned["datetime"] = pd.to_datetime(df_cleaned["datetime"], errors="coerce")
    null_dates = df_cleaned["datetime"].isna().sum()
    df_cleaned = df_cleaned.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)

    # 3. Duplicate handling
    duplicate_rows = df_cleaned.duplicated(subset=["datetime"]).sum()
    if duplicate_rows > 0:
        df_cleaned = df_cleaned.drop_duplicates(subset=["datetime"], keep="last").reset_index(drop=True)

    # 4. Numeric conversion
    for col in ["open", "high", "low", "close", "volume"]:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce")

    # 5. Missing values check & forward-fill (max limit 3 days)
    null_prices_before = df_cleaned[["open", "high", "low", "close"]].isna().sum().to_dict()
    df_cleaned[["open", "high", "low", "close"]] = df_cleaned[["open", "high", "low", "close"]].ffill(limit=3)
    df_cleaned["volume"] = df_cleaned["volume"].fillna(0.0)
    df_cleaned = df_cleaned.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)

    # 6. OHLC Relationship Validation & Repair
    # Rules: High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close
    invalid_hl = (df_cleaned["high"] < df_cleaned["low"]).sum()
    invalid_ho = (df_cleaned["high"] < df_cleaned["open"]).sum()
    invalid_hc = (df_cleaned["high"] < df_cleaned["close"]).sum()
    invalid_lo = (df_cleaned["low"] > df_cleaned["open"]).sum()
    invalid_lc = (df_cleaned["low"] > df_cleaned["close"]).sum()
    negative_volume = (df_cleaned["volume"] < 0).sum()

    # Data hygiene correction
    df_cleaned["high"] = df_cleaned[["high", "open", "close"]].max(axis=1)
    df_cleaned["low"] = df_cleaned[["low", "open", "close"]].min(axis=1)
    df_cleaned["volume"] = df_cleaned["volume"].clip(lower=0)

    # 7. Abnormal Observation Detection
    # Calculate simple returns and log returns
    df_cleaned["daily_return"] = df_cleaned["close"].pct_change().fillna(0.0)
    df_cleaned["log_return"] = np.log(df_cleaned["close"] / df_cleaned["close"].shift(1)).fillna(0.0)
    df_cleaned["cumulative_return"] = (1 + df_cleaned["daily_return"]).cumprod() - 1.0

    # Detect extreme price fluctuations (> 25% single day change)
    extreme_returns = (df_cleaned["daily_return"].abs() > 0.25).sum()
    zero_volume_days = (df_cleaned["volume"] == 0).sum()

    quality_metrics = {
        "symbol": symbol,
        "initial_rows": int(initial_rows),
        "cleaned_rows": int(len(df_cleaned)),
        "start_date": str(df_cleaned["datetime"].min().date()) if len(df_cleaned) > 0 else None,
        "end_date": str(df_cleaned["datetime"].max().date()) if len(df_cleaned) > 0 else None,
        "null_dates": int(null_dates),
        "duplicates_removed": int(duplicate_rows),
        "null_prices_repaired": {k: int(v) for k, v in null_prices_before.items()},
        "ohlc_violations_repaired": {
            "high_less_than_low": int(invalid_hl),
            "high_less_than_open": int(invalid_ho),
            "high_less_than_close": int(invalid_hc),
            "low_greater_than_open": int(invalid_lo),
            "low_greater_than_close": int(invalid_lc),
            "negative_volume": int(negative_volume)
        },
        "extreme_returns_count": int(extreme_returns),
        "zero_volume_days": int(zero_volume_days),
        "mean_daily_return": float(df_cleaned["daily_return"].mean()),
        "annualized_volatility": float(df_cleaned["daily_return"].std() * np.sqrt(252)),
    }

    # Format datetime as ISO string YYYY-MM-DD
    df_cleaned["datetime_str"] = df_cleaned["datetime"].dt.strftime("%Y-%m-%d")

    return df_cleaned, quality_metrics


def process_indices_raw_data() -> Dict[str, pd.DataFrame]:
    """
    Extracts, normalizes, and cleans major indices from backend/data/raw/NSE_Daily_indices_data.csv.
    """
    raw_indices_file = os.path.join(RAW_DIR, "NSE_Daily_indices_data.csv")
    if not os.path.exists(raw_indices_file):
        raise FileNotFoundError(f"Raw indices file not found at {raw_indices_file}")

    logger.info("Loading raw indices CSV dataset...")
    df_all = pd.read_csv(raw_indices_file)

    processed_indices = {}

    for clean_name, meta in INDICES_METADATA.items():
        raw_sym = meta["raw_symbol"]
        df_sub = df_all[df_all["SYMBOL"] == raw_sym].copy()
        if df_sub.empty:
            logger.warning(f"No records found for index symbol: {raw_sym}")
            continue

        # In this dataset: DATETIME is DD-MM-YYYY
        df_sub["DATETIME"] = pd.to_datetime(df_sub["DATETIME"], format="%d-%m-%Y", errors="coerce")
        df_sub = df_sub.sort_values("DATETIME")
        
        # Filter from 2018 onwards for alignment with stock history
        df_sub = df_sub[df_sub["DATETIME"] >= "2018-01-01"].copy()

        cleaned_df, quality = clean_and_normalize_ohlcv(
            df=df_sub,
            symbol=clean_name,
            datetime_col="DATETIME",
            open_col="OPEN",
            high_col="HIGH",
            low_col="LOW",
            close_col="CLOSE",
            volume_col="VOLUME"
        )
        processed_indices[clean_name] = (cleaned_df, quality)
        logger.info(f"Processed index {clean_name}: {len(cleaned_df)} rows")

    return processed_indices


def run_complete_data_pipeline():
    """
    Executes end-to-end data ingestion, validation, and storage.
    Outputs cleaned files in backend/data/processed/ and quality report in backend/data/reports/.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 1. Download stocks raw data if not already downloaded
    logger.info("Step 1: Downloading raw stock data...")
    download_raw_stock_data()

    quality_reports = {}

    # 2. Process Stocks
    logger.info("Step 2: Processing stock datasets...")
    for symbol in STOCKS_METADATA.keys():
        raw_path = os.path.join(RAW_STOCKS_DIR, f"{symbol}_raw.csv")
        if not os.path.exists(raw_path):
            logger.warning(f"Raw file missing for {symbol}")
            continue

        raw_df = pd.read_csv(raw_path)
        cleaned_df, quality = clean_and_normalize_ohlcv(
            df=raw_df,
            symbol=symbol,
            datetime_col="Date",
            open_col="Open",
            high_col="High",
            low_col="Low",
            close_col="Close",
            volume_col="Volume"
        )
        # Save both parquet and csv
        cleaned_df.to_parquet(os.path.join(PROCESSED_DIR, f"{symbol}.parquet"), index=False)
        cleaned_df.to_csv(os.path.join(PROCESSED_DIR, f"{symbol}.csv"), index=False)
        quality_reports[symbol] = quality

    # 3. Process Indices
    logger.info("Step 3: Processing indices dataset...")
    indices_dict = process_indices_raw_data()
    for clean_name, (cleaned_df, quality) in indices_dict.items():
        safe_name = clean_name.replace(" ", "_")
        cleaned_df.to_parquet(os.path.join(PROCESSED_DIR, f"{safe_name}.parquet"), index=False)
        cleaned_df.to_csv(os.path.join(PROCESSED_DIR, f"{safe_name}.csv"), index=False)
        quality_reports[clean_name] = quality

    # 4. Save Data Quality Report
    report_path = os.path.join(REPORTS_DIR, "data_quality_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(quality_reports, f, indent=2)

    logger.info(f"Pipeline complete! Saved data quality report to {report_path}")
    return quality_reports


if __name__ == "__main__":
    run_complete_data_pipeline()
