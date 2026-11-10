import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Activity, AlertCircle, BarChart3, ShieldCheck } from 'lucide-react';
import { apiService } from '../services/api';
import type { IndexOverview, StockSummary, CandleBar } from '../types';
import { TradingViewCandlestickChart } from '../charts/TradingViewCandlestickChart';

interface MarketOverviewProps {
  onSelectStock: (symbol: string) => void;
}

export const MarketOverviewPage: React.FC<MarketOverviewProps> = ({ onSelectStock }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overviewData, setOverviewData] = useState<{
    timestamp_status: string;
    market_sentiment: string;
    indices: IndexOverview[];
    top_gainers: StockSummary[];
    top_losers: StockSummary[];
    watchlist_symbols: string[];
  } | null>(null);

  const [niftyCandles, setNiftyCandles] = useState<CandleBar[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [overview, candlesRes] = await Promise.all([
          apiService.getMarketOverview(),
          apiService.getStockHistory('NIFTY_50', 120),
        ]);
        setOverviewData(overview);
        setNiftyCandles(candlesRes.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load market overview');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Loading Quantitative Market Stream...</p>
        </div>
      </div>
    );
  }

  if (error || !overviewData) {
    return (
      <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-6 text-center my-6">
        <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-red-200">Market Data Ingestion Error</h3>
        <p className="text-xs text-red-300/80 font-mono mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Session Header & Disclosure */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-slate-900/90 border border-terminal-border p-4 rounded-xl gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white font-mono">National Stock Exchange (NSE) Overview</h1>
            <span
              className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                overviewData.market_sentiment === 'Bullish'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : overviewData.market_sentiment === 'Bearish'
                  ? 'bg-red-950 text-red-400 border border-red-800'
                  : 'bg-slate-800 text-slate-300 border border-slate-700'
              }`}
            >
              {overviewData.market_sentiment} Bias
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            {overviewData.timestamp_status}
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 bg-cyan-950/30 border border-cyan-800/50 px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4" />
          <span>Historical Analytics Feed</span>
        </div>
      </div>

      {/* Benchmark Indices Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {overviewData.indices.map((idx) => {
          const isPos = idx.percent_change >= 0;
          return (
            <div
              key={idx.index_name}
              className="bg-terminal-surface border border-terminal-border hover:border-slate-700 rounded-xl p-4 transition shadow-sm"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-mono font-semibold text-slate-300 truncate">{idx.index_name}</span>
                <span className="text-[10px] font-mono text-slate-500">{idx.symbol}</span>
              </div>
              <div className="text-xl font-bold font-mono text-white">
                ₹{idx.latest_close.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div className="flex items-center space-x-1.5 mt-1 text-xs font-mono">
                {isPos ? (
                  <TrendingUp className="w-3.5 h-3.5 text-market-green" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5 text-market-red" />
                )}
                <span className={isPos ? 'text-market-green font-semibold' : 'text-market-red font-semibold'}>
                  {isPos ? '+' : ''}
                  {idx.percent_change.toFixed(2)}%
                </span>
                <span className="text-slate-500">
                  ({isPos ? '+' : ''}
                  {idx.change.toFixed(2)})
                </span>
              </div>
              <div className="mt-2 pt-2 border-t border-slate-800/80 flex justify-between text-[10px] font-mono text-slate-400">
                <span>H: ₹{idx.high.toLocaleString('en-IN')}</span>
                <span>L: ₹{idx.low.toLocaleString('en-IN')}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Benchmark Candlestick Chart */}
      <div className="space-y-2">
        <TradingViewCandlestickChart data={niftyCandles} symbol="NIFTY 50 Benchmark" height={400} />
      </div>

      {/* Market Movers: Gainers & Losers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-terminal-border text-xs font-mono text-emerald-400 font-bold uppercase">
            <TrendingUp className="w-4 h-4" />
            <span>Top Performing NSE Equities</span>
          </div>
          <div className="space-y-2">
            {overviewData.top_gainers.map((stock) => (
              <div
                key={stock.symbol}
                onClick={() => onSelectStock(stock.symbol)}
                className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 hover:bg-slate-800/60 border border-slate-800/60 cursor-pointer transition"
              >
                <div>
                  <div className="font-mono font-bold text-xs text-white">{stock.symbol}</div>
                  <div className="text-[11px] text-slate-400 truncate max-w-[200px]">{stock.name}</div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-bold text-white">₹{stock.latest_price.toLocaleString('en-IN')}</div>
                  <div className="text-xs text-market-green font-semibold">+{stock.change_percent.toFixed(2)}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Losers */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-terminal-border text-xs font-mono text-rose-400 font-bold uppercase">
            <TrendingDown className="w-4 h-4" />
            <span>Underperforming NSE Equities</span>
          </div>
          <div className="space-y-2">
            {overviewData.top_losers.map((stock) => (
              <div
                key={stock.symbol}
                onClick={() => onSelectStock(stock.symbol)}
                className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 hover:bg-slate-800/60 border border-slate-800/60 cursor-pointer transition"
              >
                <div>
                  <div className="font-mono font-bold text-xs text-white">{stock.symbol}</div>
                  <div className="text-[11px] text-slate-400 truncate max-w-[200px]">{stock.name}</div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-bold text-white">₹{stock.latest_price.toLocaleString('en-IN')}</div>
                  <div className="text-xs text-market-red font-semibold">{stock.change_percent.toFixed(2)}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
