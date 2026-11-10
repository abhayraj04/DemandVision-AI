# MarketVision AI — REST API Specification

Base URL: `http://localhost:8000/api` or `/api`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service uptime, engine status, and data source disclosure |
| `GET` | `/market/overview` | NIFTY 50, NIFTY BANK, NIFTY IT, NIFTY NEXT 50, INDIA VIX, top movers |
| `GET` | `/stocks` | List of 10 supported NSE equities with 52-week bounds and quotes |
| `GET` | `/stocks/{symbol}` | In-depth company profile and performance quote |
| `GET` | `/stocks/{symbol}/history?limit={n}` | OHLCV candlestick series for TradingView charting |
| `GET` | `/stocks/{symbol}/indicators?limit={n}` | Technical indicator time series, active signals, educational metadata |
| `GET` | `/stocks/{symbol}/forecast` | 7-day, 14-day, 30-day forecast packages with 95% confidence bounds |
| `GET` | `/stocks/{symbol}/risk` | Volatility, Max Drawdown, VaR (95%/99%), CVaR, Sharpe, Sortino, Beta |
| `POST` | `/portfolio/analyze` | Dynamic multi-asset portfolio risk and diversification simulation |
| `GET` | `/models/performance` | Model leaderboard across Naive, MA20, ARIMA, SARIMAX, and XGBoost |
| `GET` | `/insights/{symbol}` | Deterministic quantitative AI insights synthesized from real metrics |
