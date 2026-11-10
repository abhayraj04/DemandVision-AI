"""
Phase 5 Test Suite: XGBoost Machine Learning and Model Evaluation Center
"""
import os
import json
import numpy as np
import pandas as pd
import pytest

from backend.forecasting.ml_models import create_lagged_features, train_and_evaluate_xgboost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "data", "models")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
FEATURES_DIR = os.path.join(BASE_DIR, "data", "features")


def test_lagged_features_creation():
    df_feat = pd.read_parquet(os.path.join(FEATURES_DIR, "RELIANCE_features.parquet"))
    clean_data, feature_cols = create_lagged_features(df_feat)
    assert len(feature_cols) >= 10, "Expected at least 10 lagged features"
    assert "target_return" in clean_data.columns
    assert "ret_lag1" in feature_cols
    assert "volume_ratio" in feature_cols
    assert clean_data[feature_cols].isna().sum().sum() == 0, "Found NaN in features"


def test_xgboost_training_and_artifacts():
    res = train_and_evaluate_xgboost("RELIANCE")
    assert "metrics" in res
    assert res["metrics"]["rmse"] > 0
    assert "feature_importances" in res
    assert len(res["feature_importances"]) > 0
    assert "residual_stats" in res
    assert abs(res["residual_stats"]["mean_error"]) < 50.0  # reasonable residual mean

    # Check joblib artifact exists
    joblib_path = os.path.join(MODELS_DIR, "RELIANCE_xgboost.joblib")
    assert os.path.exists(joblib_path), "Model artifact joblib missing"


def test_model_leaderboard_integrity():
    leaderboard_file = os.path.join(REPORTS_DIR, "model_leaderboard.json")
    assert os.path.exists(leaderboard_file), "Leaderboard file missing"
    with open(leaderboard_file, "r") as f:
        board = json.load(f)

    target_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "AXISBANK", "BHARTIARTL", "NIFTY_50"]
    for sym in target_symbols:
        assert sym in board, f"Symbol {sym} missing from leaderboard"
        entry = board[sym]
        assert "best_model" in entry
        assert "selection_rationale" in entry
        assert "models" in entry
        assert len(entry["models"]) == 5  # Naive, MA20, ARIMA, SARIMAX, XGBoost
        assert "feature_importances" in entry
        assert "residual_stats" in entry
