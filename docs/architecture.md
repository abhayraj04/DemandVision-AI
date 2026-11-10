# MarketVision AI — Technical Architecture Specification

## 1. Multi-Tier System Architecture

```mermaid
flowchart TD
    subgraph Data Layer [Data Engineering Pipeline]
        RawData["Raw Historical NSE Datasets (CSV & yfinance)"] --> Sanitizer["Validation & Sanitization Engine"]
        Sanitizer --> Cleaner["Immutability Check & OHLC Geometric Guard"]
        Cleaner --> Storage["Processed Dual Persistence (.parquet & .csv)"]
    end

    subgraph Feature & Analytics [Quantitative Computation Engine]
        Storage --> Indicators["Technical Indicators (SMA, EMA, RSI, MACD, BB, ATR, OBV)"]
        Indicators --> Signals["Deterministic Analytical Signals"]
        Storage --> Risk["Risk Analytics (VaR, CVaR, MDD, Sharpe, Sortino, CAPM Beta)"]
    end

    subgraph Modeling [Forecasting & ML Center]
        Storage --> Splitter["Chronological Partitioning (No Lookahead)"]
        Splitter --> StatsModels["Statistical Suite (Naive, MA20, ARIMA, SARIMAX)"]
        Splitter --> XGB["XGBoost Lagged Multi-Factor Regressor"]
        StatsModels --> WFV["Walk-Forward Validation"]
        XGB --> WFV
        WFV --> Leaderboard["Occam's Principle Leaderboard Engine"]
    end

    subgraph API [FastAPI REST Gateway]
        Leaderboard --> APIEndpoints["FastAPI In-Memory Cached Endpoints"]
        Risk --> APIEndpoints
        Signals --> APIEndpoints
        APIEndpoints --> Swagger["Interactive OpenAPI /docs & ReDoc"]
    end

    subgraph Client [React 19 Frontend Terminal]
        APIEndpoints --> ReactApp["React 19 + TypeScript Terminal Client"]
        ReactApp --> LightweightCharts["TradingView Lightweight Candlestick Charts"]
        ReactApp --> Recharts["Recharts Multi-Horizon & Underwater Visualizations"]
    end
```

## 2. Quantitative Design Decisions

### Data Leakage Safeguards
1. **Chronological Splitting**: Under no circumstances are random train/test splits used for temporal financial series.
2. **Standardization Isolation**: Preprocessing scaling (`StandardScaler`) parameters are derived strictly from training windows and applied out-of-sample.
3. **Walk-Forward Validation**: Multi-step walk-forward cross-validation evaluates generalization error across evolving market volatility regimes.

### Occam's Razor Model Selection
- Complex nonlinear models (XGBoost) often overfit market micro-noise in efficient, near-martingale regimes.
- When statistical baselines (Naive Persistence or ARIMA differencing) achieve superior or comparable out-of-sample RMSE, the system selects the parsimonious model and provides a transparent educational rationale.
