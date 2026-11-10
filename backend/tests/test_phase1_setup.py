"""
Phase 1 Smoke Test: Environment and Architecture Verification
"""
import os
import sys

def test_python_version():
    assert sys.version_info >= (3, 10), "Python 3.10+ required"

def test_core_libraries_imported():
    import numpy as np
    import pandas as pd
    import sklearn
    import statsmodels
    import xgboost
    import arch
    import fastapi
    import uvicorn
    assert np is not None
    assert pd is not None
    assert sklearn is not None
    assert statsmodels is not None
    assert xgboost is not None
    assert arch is not None
    assert fastapi is not None
    assert uvicorn is not None

def test_directories_exist():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_dirs = [
        os.path.join(base_dir, "api"),
        os.path.join(base_dir, "data", "raw"),
        os.path.join(base_dir, "data", "processed"),
        os.path.join(base_dir, "data", "features"),
        os.path.join(base_dir, "data", "predictions"),
        os.path.join(base_dir, "data", "models"),
        os.path.join(base_dir, "data", "reports"),
        os.path.join(base_dir, "preprocessing"),
        os.path.join(base_dir, "features"),
        os.path.join(base_dir, "analysis"),
        os.path.join(base_dir, "forecasting"),
        os.path.join(base_dir, "risk"),
        os.path.join(base_dir, "insights"),
    ]
    for d in required_dirs:
        assert os.path.isdir(d), f"Directory {d} missing"

def test_raw_dataset_exists():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_csv = os.path.join(base_dir, "data", "raw", "NSE_Daily_indices_data.csv")
    assert os.path.exists(raw_csv), f"Raw dataset missing at {raw_csv}"
    assert os.path.getsize(raw_csv) > 1000000, "Raw dataset file is surprisingly small"
