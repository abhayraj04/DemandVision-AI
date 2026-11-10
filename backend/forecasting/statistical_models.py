"""
MarketVision AI - Statistical Time-Series Forecasting Module
Implements Naive, Rolling Moving Average, ARIMA, and SARIMA forecasting models
with chronological walk-forward validation and statistical confidence intervals.
"""

import os
import json
import logging
import warnings
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import joblib

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PREDICTIONS_DIR = os.path.join(BASE_DIR, "data", "predictions")
MODELS_DIR = os.path.join(BASE_DIR, "data", "models")


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_base: Optional[np.ndarray] = None) -> Dict[str, float]:
    """
    Computes standard institutional forecasting accuracy metrics:
    MAE, RMSE, MAPE (safe division), Directional Accuracy, and R2.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true = y_true[mask]
    y_pred = y_pred[mask]

    if len(y_true) == 0:
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0, "directional_accuracy": 50.0, "r2": 0.0}

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    # Safe MAPE with epsilon
    epsilon = 1e-5
    mape = float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + epsilon))) * 100.0)

    # Directional Accuracy
    if y_base is not None and len(y_base) == len(y_true):
        y_base = np.asarray(y_base)[mask]
        actual_direction = np.sign(y_true - y_base)
        pred_direction = np.sign(y_pred - y_base)
        dir_acc = float(np.mean(actual_direction == pred_direction) * 100.0)
    else:
        # Step-by-step diff direction
        if len(y_true) > 1:
            actual_dir = np.sign(np.diff(y_true))
            pred_dir = np.sign(np.diff(y_pred))
            dir_acc = float(np.mean(actual_dir == pred_dir) * 100.0)
        else:
            dir_acc = 50.0

    # R2 Score
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 4),
        "directional_accuracy": round(dir_acc, 2),
        "r2": round(r2, 4)
    }


class NaiveModel:
    """Baseline persistence model: y_{t+h} = y_t."""
    def __init__(self):
        self.last_value = None
        self.resid_std = None

    def fit(self, series: pd.Series):
        self.last_value = float(series.iloc[-1])
        diffs = series.diff().dropna()
        raw_std = float(diffs.std()) if len(diffs) > 1 else 0.0
        # Ensure positive variance floor (at least 0.1% of price or 0.01)
        self.resid_std = max(raw_std, 0.001 * abs(self.last_value), 0.01)
        return self

    def forecast(self, steps: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        preds = np.full(steps, self.last_value)
        # Uncertainty grows with sqrt(h)
        step_arr = np.arange(1, steps + 1)
        stderr = self.resid_std * np.sqrt(step_arr)
        lower_95 = preds - 1.96 * stderr
        upper_95 = preds + 1.96 * stderr
        return preds, lower_95, upper_95


class MovingAverageModel:
    """Rolling moving average baseline: y_{t+h} = mean(y_{t-k:t})."""
    def __init__(self, window: int = 20):
        self.window = window
        self.mean_val = None
        self.resid_std = None

    def fit(self, series: pd.Series):
        recent = series.iloc[-self.window:]
        self.mean_val = float(recent.mean())
        residuals = series - series.rolling(self.window).mean()
        raw_std = float(residuals.dropna().std()) if len(residuals.dropna()) > 1 else 0.0
        self.resid_std = max(raw_std, 0.001 * abs(self.mean_val), 0.01)
        return self

    def forecast(self, steps: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        preds = np.full(steps, self.mean_val)
        step_arr = np.arange(1, steps + 1)
        stderr = self.resid_std * np.sqrt(step_arr)
        lower_95 = preds - 1.96 * stderr
        upper_95 = preds + 1.96 * stderr
        return preds, lower_95, upper_95


class ARIMAModel:
    """ARIMA(p, d, q) statistical model with analytical confidence intervals."""
    def __init__(self, order: Tuple[int, int, int] = (2, 1, 2)):
        self.order = order
        self.model_res = None
        self.history = None

    def fit(self, series: pd.Series):
        self.history = series.copy()
        try:
            model = ARIMA(series, order=self.order)
            self.model_res = model.fit()
        except Exception as e:
            logger.warning(f"ARIMA{self.order} fit failed ({e}), falling back to ARIMA(1, 1, 1)")
            self.order = (1, 1, 1)
            model = ARIMA(series, order=self.order)
            self.model_res = model.fit()
        return self

    def forecast(self, steps: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        fc = self.model_res.get_forecast(steps=steps)
        preds = fc.predicted_mean.values
        conf_int = fc.conf_int(alpha=0.05).values
        lower_95 = conf_int[:, 0]
        upper_95 = conf_int[:, 1]
        return preds, lower_95, upper_95


class SARIMAXModel:
    """SARIMAX(p, d, q) x (P, D, Q)_5 seasonal model for weekly NSE trading cycles."""
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1), seasonal_order: Tuple[int, int, int, int] = (1, 0, 1, 5)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.model_res = None

    def fit(self, series: pd.Series):
        # Fit on last 500 trading observations for stability and computational efficiency
        train_slice = series.iloc[-500:] if len(series) > 500 else series
        try:
            model = SARIMAX(train_slice, order=self.order, seasonal_order=self.seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
            self.model_res = model.fit(disp=False, maxiter=50)
        except Exception as e:
            logger.warning(f"SARIMAX fit failed ({e}), falling back to SARIMAX(1, 1, 0)x(0, 0, 0, 5)")
            model = SARIMAX(train_slice, order=(1, 1, 0), seasonal_order=(0, 0, 0, 5), enforce_stationarity=False, enforce_invertibility=False)
            self.model_res = model.fit(disp=False, maxiter=50)
        return self

    def forecast(self, steps: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        fc = self.model_res.get_forecast(steps=steps)
        preds = fc.predicted_mean.values
        conf_int = fc.conf_int(alpha=0.05).values
        lower_95 = conf_int[:, 0]
        upper_95 = conf_int[:, 1]
        return preds, lower_95, upper_95


def perform_walk_forward_validation(
    series: pd.Series,
    test_window: int = 60,
    forecast_horizon: int = 14
) -> Dict[str, Any]:
    """
    Executes chronological walk-forward out-of-sample validation.
    Splits data chronologically without random shuffling or data leakage.
    Evaluates: Naive, Moving Average (20), ARIMA(2, 1, 2), SARIMAX(1, 1, 1)x(1, 0, 1, 5).
    """
    n = len(series)
    train_end = n - test_window
    train_series = series.iloc[:train_end]
    test_series = series.iloc[train_end:]

    actual_values = test_series.iloc[:forecast_horizon].values
    y_base = np.full(len(actual_values), train_series.iloc[-1])

    # 1. Naive Model
    naive = NaiveModel().fit(train_series)
    naive_preds, _, _ = naive.forecast(steps=forecast_horizon)
    naive_metrics = calculate_metrics(actual_values, naive_preds, y_base)

    # 2. Moving Average (20)
    ma_model = MovingAverageModel(window=20).fit(train_series)
    ma_preds, _, _ = ma_model.forecast(steps=forecast_horizon)
    ma_metrics = calculate_metrics(actual_values, ma_preds, y_base)

    # 3. ARIMA
    arima_model = ARIMAModel(order=(2, 1, 2)).fit(train_series)
    arima_preds, _, _ = arima_model.forecast(steps=forecast_horizon)
    arima_metrics = calculate_metrics(actual_values, arima_preds, y_base)

    # 4. SARIMAX
    sarimax_model = SARIMAXModel(order=(1, 1, 1), seasonal_order=(1, 0, 1, 5)).fit(train_series)
    sarimax_preds, _, _ = sarimax_model.forecast(steps=forecast_horizon)
    sarimax_metrics = calculate_metrics(actual_values, sarimax_preds, y_base)

    comparison = {
        "Naive": {"metrics": naive_metrics, "predictions": naive_preds.tolist()},
        "Moving_Average_20": {"metrics": ma_metrics, "predictions": ma_preds.tolist()},
        "ARIMA_2_1_2": {"metrics": arima_metrics, "predictions": arima_preds.tolist()},
        "SARIMAX_Weekly": {"metrics": sarimax_metrics, "predictions": sarimax_preds.tolist()},
    }

    # Best model by RMSE
    best_model_name = min(comparison.keys(), key=lambda k: comparison[k]["metrics"]["rmse"])

    return {
        "validation_horizon": forecast_horizon,
        "test_actuals": actual_values.tolist(),
        "comparison": comparison,
        "best_model": best_model_name
    }


def generate_future_trading_dates(last_date: pd.Timestamp, num_days: int) -> List[str]:
    """Generates future weekday trading dates."""
    dates = []
    curr = last_date
    while len(dates) < num_days:
        curr += pd.Timedelta(days=1)
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr.strftime("%Y-%m-%d"))
    return dates


def build_stock_forecast_package(symbol: str) -> Dict[str, Any]:
    """
    Computes full forecasting package for a given symbol:
    - Chronological walk-forward validation
    - Multi-horizon forecasts (7, 14, 30 days) with confidence intervals
    - Actual vs Predicted historical tracking
    """
    parquet_path = os.path.join(PROCESSED_DIR, f"{symbol}.parquet")
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Processed file missing for {symbol}")

    df = pd.read_parquet(parquet_path)
    close_series = df["close"]
    last_date = pd.to_datetime(df["datetime"].iloc[-1])
    last_close = float(close_series.iloc[-1])

    # 1. Walk-Forward Validation
    wfv_results = perform_walk_forward_validation(close_series, test_window=45, forecast_horizon=14)

    # 2. Refit on entire dataset for production future forecasts
    arima = ARIMAModel(order=(2, 1, 2)).fit(close_series)
    sarimax = SARIMAXModel().fit(close_series)
    naive = NaiveModel().fit(close_series)

    # Multi-horizon forecasts: 30 days covers 7, 14, and 30
    steps = 30
    future_dates = generate_future_trading_dates(last_date, steps)
    arima_preds, arima_lower, arima_upper = arima.forecast(steps)
    sarimax_preds, sarimax_lower, sarimax_upper = sarimax.forecast(steps)
    naive_preds, naive_lower, naive_upper = naive.forecast(steps)

    def package_horizon(h_steps: int):
        sub_dates = future_dates[:h_steps]
        sub_arima = arima_preds[:h_steps]
        sub_lower = arima_lower[:h_steps]
        sub_upper = arima_upper[:h_steps]
        
        target_pred_price = float(sub_arima[-1])
        expected_return_pct = round(((target_pred_price - last_close) / last_close) * 100.0, 2)
        direction = "BULLISH" if expected_return_pct > 0 else "BEARISH"

        forecast_points = []
        for d, p, l, u in zip(sub_dates, sub_arima, sub_lower, sub_upper):
            forecast_points.append({
                "date": d,
                "predicted_close": round(float(p), 2),
                "lower_bound_95": round(float(l), 2),
                "upper_bound_95": round(float(u), 2),
            })

        return {
            "horizon_days": h_steps,
            "target_date": sub_dates[-1],
            "target_predicted_price": round(target_pred_price, 2),
            "current_price": round(last_close, 2),
            "expected_return_pct": expected_return_pct,
            "projected_direction": direction,
            "forecast_series": forecast_points
        }

    forecasts_by_horizon = {
        "7_day": package_horizon(7),
        "14_day": package_horizon(14),
        "30_day": package_horizon(30),
    }

    # Recent historical actuals (last 60 days) for actual vs predicted visualization
    recent_history = []
    for _, row in df.iloc[-60:].iterrows():
        recent_history.append({
            "date": row["datetime_str"],
            "actual_close": round(float(row["close"]), 2),
            "volume": float(row["volume"]),
        })

    package = {
        "symbol": symbol,
        "last_updated": df["datetime_str"].iloc[-1],
        "current_price": round(last_close, 2),
        "walk_forward_validation": wfv_results,
        "horizons": forecasts_by_horizon,
        "recent_history": recent_history,
        "uncertainty_disclaimer": "Forecasts represent statistical conditional expectations and confidence bounds based on historical price dynamics. Financial markets possess inherent stochastic volatility; these projections do not guarantee future performance and are strictly for quantitative research."
    }

    return package


def process_and_save_all_forecasts():
    """Generates and saves statistical forecasting packages for all 10 stocks and NIFTY 50."""
    os.makedirs(PREDICTIONS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL", "NIFTY_50"]

    summary = {}
    for sym in symbols:
        logger.info(f"Generating statistical forecasts for {sym}...")
        package = build_stock_forecast_package(sym)
        dest_path = os.path.join(PREDICTIONS_DIR, f"{sym}_forecast.json")
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2)

        summary[sym] = {
            "current_price": package["current_price"],
            "best_validation_model": package["walk_forward_validation"]["best_model"],
            "best_rmse": package["walk_forward_validation"]["comparison"][package["walk_forward_validation"]["best_model"]]["metrics"]["rmse"],
            "7d_expected_return": package["horizons"]["7_day"]["expected_return_pct"],
            "30d_expected_return": package["horizons"]["30_day"]["expected_return_pct"],
        }

    summary_file = os.path.join(PREDICTIONS_DIR, "forecast_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("Forecasting pipeline complete!")
    return summary


if __name__ == "__main__":
    summary = process_and_save_all_forecasts()
    print("Forecasting generation completed for:", list(summary.keys()))
