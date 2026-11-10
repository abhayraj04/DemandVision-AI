"""
Phase 4 Test Suite: Statistical Forecasting & Chronological Walk-Forward Validation
"""
import os
import json
import numpy as np
import pandas as pd
import pytest

from backend.forecasting.statistical_models import (
    calculate_metrics, NaiveModel, MovingAverageModel, ARIMAModel,
    perform_walk_forward_validation
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREDICTIONS_DIR = os.path.join(BASE_DIR, "data", "predictions")


def test_metrics_calculation():
    y_true = np.array([100.0, 105.0, 102.0, 110.0])
    y_pred = np.array([102.0, 104.0, 100.0, 108.0])
    m = calculate_metrics(y_true, y_pred)
    assert "mae" in m and m["mae"] > 0
    assert "rmse" in m and m["rmse"] >= m["mae"]
    assert "mape" in m and m["mape"] > 0
    assert "directional_accuracy" in m
    assert "r2" in m


def test_naive_forecaster():
    series = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    naive = NaiveModel().fit(series)
    preds, lower, upper = naive.forecast(steps=5)
    assert len(preds) == 5
    assert (preds == 14.0).all()
    assert (lower < preds).all()
    assert (upper > preds).all()
    # Confidence interval width must expand with sqrt(h)
    width = upper - lower
    assert np.all(np.diff(width) > 0)


def test_moving_average_forecaster():
    series = pd.Series([10.0, 20.0, 30.0, 40.0])
    ma = MovingAverageModel(window=3).fit(series)
    preds, lower, upper = ma.forecast(steps=4)
    # mean of last 3 items: (20 + 30 + 40) / 3 = 30.0
    assert np.isclose(preds[0], 30.0)
    assert (lower < preds).all()


def test_arima_forecaster():
    np.random.seed(42)
    series = pd.Series(np.cumsum(np.random.normal(0.5, 2.0, 100)) + 500)
    arima = ARIMAModel(order=(1, 1, 1)).fit(series)
    preds, lower, upper = arima.forecast(steps=10)
    assert len(preds) == 10
    assert (lower < upper).all()


def test_saved_forecast_packages():
    target_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL"]
    for sym in target_stocks:
        json_path = os.path.join(PREDICTIONS_DIR, f"{sym}_forecast.json")
        assert os.path.exists(json_path), f"Forecast JSON missing for {sym}"
        with open(json_path, "r") as f:
            data = json.load(f)
        assert "walk_forward_validation" in data
        assert "horizons" in data
        assert "7_day" in data["horizons"]
        assert "14_day" in data["horizons"]
        assert "30_day" in data["horizons"]
        assert len(data["horizons"]["30_day"]["forecast_series"]) == 30
        assert "uncertainty_disclaimer" in data
