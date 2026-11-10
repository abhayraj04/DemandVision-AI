import type {
  IndexOverview,
  StockSummary,
  StockItem,
  CandleBar,
  IndicatorDataPoint,
  AnalyticalSignal,
  ForecastPackage,
  RiskProfile,
  PortfolioSimulation,
  LeaderboardEntry,
  AIInsights
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP Error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err: any) {
    console.error(`API Fetch Failure [${endpoint}]:`, err);
    throw err;
  }
}

export const apiService = {
  getHealth: () => fetchJSON<{ status: string; service: string }>('/api/health'),

  getMarketOverview: () => fetchJSON<{
    timestamp_status: string;
    market_sentiment: string;
    indices: IndexOverview[];
    top_gainers: StockSummary[];
    top_losers: StockSummary[];
    watchlist_symbols: string[];
  }>('/api/market/overview'),

  getStocks: () => fetchJSON<{ count: number; stocks: StockItem[] }>('/api/stocks'),

  getStockProfile: (symbol: string) => fetchJSON<any>(`/api/stocks/${symbol}`),

  getStockHistory: (symbol: string, limit: number = 250) =>
    fetchJSON<{ symbol: string; count: number; data: CandleBar[] }>(`/api/stocks/${symbol}/history?limit=${limit}`),

  getStockIndicators: (symbol: string, limit: number = 120) =>
    fetchJSON<{
      symbol: string;
      active_signals: AnalyticalSignal[];
      indicator_catalog: Record<string, any>;
      history: IndicatorDataPoint[];
    }>(`/api/stocks/${symbol}/indicators?limit=${limit}`),

  getStockForecast: (symbol: string) => fetchJSON<ForecastPackage>(`/api/stocks/${symbol}/forecast`),

  getStockRisk: (symbol: string) =>
    fetchJSON<{ profile: RiskProfile; metric_definitions: Record<string, any> }>(`/api/stocks/${symbol}/risk`),

  analyzePortfolio: (weights: Record<string, number>, riskFreeRate: number = 0.065) =>
    fetchJSON<PortfolioSimulation>('/api/portfolio/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ weights, risk_free_rate: riskFreeRate }),
    }),

  getModelsPerformance: () =>
    fetchJSON<{ leaderboard: Record<string, LeaderboardEntry>; evaluation_criteria: any }>('/api/models/performance'),

  getAIInsights: (symbol: string) => fetchJSON<AIInsights>(`/api/insights/${symbol}`),
};
