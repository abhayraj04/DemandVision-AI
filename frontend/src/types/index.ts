export interface IndexOverview {
  index_name: string;
  symbol: string;
  sector: string;
  latest_close: number;
  open: number;
  high: number;
  low: number;
  change: number;
  percent_change: number;
  volume: number;
  last_timestamp: string;
  trend: "Bullish" | "Bearish" | "Neutral";
}

export interface StockSummary {
  symbol: string;
  name: string;
  sector: string;
  latest_price: number;
  change_percent: number;
  volume: number;
  last_updated: string;
}

export interface StockItem {
  symbol: string;
  ticker: string;
  name: string;
  sector: string;
  benchmark: string;
  latest_close: number;
  change: number;
  change_percent: number;
  volume: number;
  high_52w: number;
  low_52w: number;
  last_traded_date: string;
}

export interface CandleBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  daily_return: number;
}

export interface AnalyticalSignal {
  indicator: string;
  condition: string;
  bias: "BULLISH_BIAS" | "BEARISH_BIAS" | "NEUTRAL";
  value: number;
  detail: string;
}

export interface IndicatorDataPoint {
  date: string;
  close: number;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  ema_9?: number;
  ema_21?: number;
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
  bb_bandwidth?: number;
  atr_14?: number;
  obv?: number;
}

export interface ForecastPoint {
  date: string;
  predicted_close: number;
  lower_bound_95: number;
  upper_bound_95: number;
}

export interface ForecastHorizon {
  horizon_days: number;
  target_date: string;
  target_predicted_price: number;
  current_price: number;
  expected_return_pct: number;
  projected_direction: "BULLISH" | "BEARISH";
  forecast_series: ForecastPoint[];
}

export interface ForecastPackage {
  symbol: string;
  last_updated: string;
  current_price: number;
  walk_forward_validation: {
    validation_horizon: number;
    test_actuals: number[];
    comparison: Record<string, {
      metrics: {
        mae: number;
        rmse: number;
        mape: number;
        directional_accuracy: number;
        r2: number;
      };
      predictions: number[];
    }>;
    best_model: string;
  };
  horizons: {
    "7_day": ForecastHorizon;
    "14_day": ForecastHorizon;
    "30_day": ForecastHorizon;
  };
  recent_history: {
    date: string;
    actual_close: number;
    volume: number;
  }[];
  uncertainty_disclaimer: string;
}

export interface RiskProfile {
  symbol: string;
  annualized_volatility: number;
  rolling_volatility_21d: number;
  rolling_volatility_63d: number;
  annualized_return_1y: number;
  max_drawdown_pct: number;
  drawdown_peak_date: string | null;
  drawdown_trough_date: string | null;
  sharpe_ratio: number;
  sortino_ratio: number;
  beta_vs_nifty50: number;
  jensens_alpha_pct: number;
  risk_free_rate_used: number;
  var_cvar: Record<string, {
    historical_var_1d: number;
    historical_cvar_1d: number;
    parametric_var_1d: number;
    cornish_fisher_var_1d: number;
    historical_var_10d: number;
  }>;
  rolling_drawdowns: {
    date: string;
    drawdown_pct: number;
  }[];
}

export interface PortfolioSimulation {
  portfolio_allocation: Record<string, number>;
  expected_annual_return: number;
  annualized_volatility: number;
  diversification_ratio: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown_pct: number;
  var_cvar: Record<string, any>;
  risk_tier: string;
}

export interface LeaderboardEntry {
  symbol: string;
  best_model: string;
  selection_rationale: string;
  models: Record<string, {
    model_family: string;
    complexity: string;
    rmse: number;
    mae: number;
    mape: number;
    directional_accuracy: number;
    r2: number;
  }>;
  feature_importances: { feature: string; importance: number }[];
  residual_stats: {
    mean_error: number;
    std_error: number;
    skewness: number;
    kurtosis: number;
  };
  recent_predictions: {
    date: string;
    actual: number;
    predicted: number;
    residual: number;
  }[];
}

export interface AIInsights {
  symbol: string;
  company_name: string;
  sector: string;
  generated_at: string;
  trend_summary: string;
  volatility_observation: string;
  volume_observation: string;
  risk_warning: string;
  forecast_explanation: string;
  overall_stance: "BULLISH_BIAS" | "BEARISH_BIAS" | "NEUTRAL_CONSOLIDATION";
  confidence_level: string;
  disclaimer: string;
}
