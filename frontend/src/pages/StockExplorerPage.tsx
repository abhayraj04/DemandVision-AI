import React, { useEffect, useState } from 'react';
import { Search, TrendingUp, TrendingDown, Layers, BarChart2, Zap, Clock } from 'lucide-react';
import { apiService } from '../services/api';
import type { StockItem, CandleBar } from '../types';
import { TradingViewCandlestickChart } from '../charts/TradingViewCandlestickChart';
import { Level2OrderBook } from '../components/Level2OrderBook';
import { OptionsAnalyticsPanel } from '../components/OptionsAnalyticsPanel';
import { LiveSentimentFeed } from '../components/LiveSentimentFeed';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

interface StockExplorerProps {
  selectedStock: string;
  onSelectStock: (symbol: string) => void;
  availableStocks: string[];
}

export const StockExplorerPage: React.FC<StockExplorerProps> = ({
  selectedStock,
  onSelectStock,
  availableStocks,
}) => {
  const [stocksList, setStocksList] = useState<StockItem[]>([]);
  const [stockProfile, setStockProfile] = useState<any>(null);
  const [candles, setCandles] = useState<CandleBar[]>([]);
  const [timeframe, setTimeframe] = useState<'1M' | '5M' | '15M' | '1H' | '1D'>('1D');
  const [loading, setLoading] = useState(true);

  // Comparison State
  const [compareStock, setCompareStock] = useState<string>('TCS');
  const [compareMode, setCompareMode] = useState<boolean>(false);
  const [comparisonData, setComparisonData] = useState<any[]>([]);

  useEffect(() => {
    async function fetchStockData() {
      try {
        setLoading(true);
        const [listRes, profRes] = await Promise.all([
          apiService.getStocks(),
          apiService.getStockProfile(selectedStock),
        ]);
        setStocksList(listRes.stocks);
        setStockProfile(profRes);

        // Fetch bars based on selected timeframe
        if (timeframe === '1D') {
          const candleRes = await apiService.getStockHistory(selectedStock, 150);
          setCandles(candleRes.data);
        } else {
          const res = await fetch(`/api/realtime/intraday/${selectedStock}?timeframe=${timeframe}&limit=60`);
          if (res.ok) {
            const data = await res.json();
            setCandles(data.data);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchStockData();
  }, [selectedStock, timeframe]);

  // Comparison loader
  useEffect(() => {
    if (!compareMode) return;
    async function loadComparison() {
      try {
        const [baseRes, compRes] = await Promise.all([
          apiService.getStockHistory(selectedStock, 90),
          apiService.getStockHistory(compareStock, 90),
        ]);

        const baseStart = baseRes.data[0]?.close || 1;
        const compStart = compRes.data[0]?.close || 1;

        const merged = baseRes.data.map((b, i) => {
          const c = compRes.data[i];
          return {
            date: b.time,
            [selectedStock]: Number((((b.close - baseStart) / baseStart) * 100).toFixed(2)),
            [compareStock]: c ? Number((((c.close - compStart) / compStart) * 100).toFixed(2)) : 0,
          };
        });
        setComparisonData(merged);
      } catch (e) {
        console.error(e);
      }
    }
    loadComparison();
  }, [compareMode, selectedStock, compareStock]);

  const currentStockMeta = stocksList.find((s) => s.symbol === selectedStock);
  const isPos = (stockProfile?.quote?.change_percent || 0) >= 0;

  return (
    <div className="space-y-6">
      {/* Stock Selection Bar & Metrics */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-terminal-border/60">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold font-mono text-white">{selectedStock}</h1>
              <span className="text-xs font-mono bg-blue-950 border border-blue-800 text-blue-300 px-2 py-0.5 rounded">
                {currentStockMeta?.sector || 'NSE Large Cap'}
              </span>
              <span className="text-xs font-mono text-slate-400">
                Benchmark: {currentStockMeta?.benchmark || 'NIFTY 50'}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1">{currentStockMeta?.name}</p>
          </div>

          {/* Quick Select Buttons */}
          <div className="flex flex-wrap gap-1.5">
            {availableStocks.map((s) => (
              <button
                key={s}
                onClick={() => onSelectStock(s)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition border ${
                  selectedStock === s
                    ? 'bg-market-cyan/20 text-market-cyan border-market-cyan/50 font-bold'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Real-time Style Key Financial Metrics Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 pt-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Last Traded Price</span>
            <span className="text-lg font-bold text-white">
              ₹{stockProfile?.quote?.current_price?.toLocaleString('en-IN') || '—'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Session Change</span>
            <span className={`text-base font-bold flex items-center ${isPos ? 'text-market-green' : 'text-market-red'}`}>
              {isPos ? '+' : ''}
              {stockProfile?.quote?.change_percent?.toFixed(2)}%
            </span>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase">52-Week High</span>
            <span className="text-sm font-semibold text-slate-200">
              ₹{stockProfile?.performance?.['52_week_high']?.toLocaleString('en-IN') || '—'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase">52-Week Low</span>
            <span className="text-sm font-semibold text-slate-200">
              ₹{stockProfile?.performance?.['52_week_low']?.toLocaleString('en-IN') || '—'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Trading Volume</span>
            <span className="text-sm font-semibold text-slate-200">
              {Number(stockProfile?.quote?.volume || 0).toLocaleString('en-IN')}
            </span>
          </div>

          <div>
            <span className="text-slate-500 block text-[10px] uppercase">Annualized Volatility</span>
            <span className="text-sm font-semibold text-market-cyan">
              {stockProfile?.performance?.annualized_volatility}%
            </span>
          </div>
        </div>
      </div>

      {/* Intraday Timeframe Bar */}
      <div className="flex items-center justify-between bg-slate-900/90 border border-terminal-border px-4 py-2 rounded-xl text-xs font-mono">
        <div className="flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400 uppercase text-[11px] font-semibold">Candlestick Resolution:</span>
          {(['1M', '5M', '15M', '1H', '1D'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-1 rounded font-bold transition border ${
                timeframe === tf
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        <div className="text-[11px] text-emerald-400 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Streaming Live Tick Aggregation</span>
        </div>
      </div>

      {/* Candlestick Chart & Level-2 Order Book Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TradingViewCandlestickChart data={candles} symbol={`${selectedStock} (${timeframe})`} height={420} />
        </div>
        <div>
          <Level2OrderBook symbol={selectedStock} liveLtp={stockProfile?.quote?.current_price} />
        </div>
      </div>

      {/* Options & Derivatives Chain Analytics */}
      <OptionsAnalyticsPanel symbol={selectedStock} />

      {/* Real-time Market Sentiment Feed */}
      <LiveSentimentFeed symbol={selectedStock} />

      {/* Cross-Stock Comparison Mode */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-terminal-border gap-3">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-white">
            <Layers className="w-4 h-4 text-market-cyan" />
            <span>Relative Return Performance Comparison (90 Sessions)</span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono">
            <button
              onClick={() => setCompareMode(!compareMode)}
              className={`px-3 py-1 rounded font-semibold transition border ${
                compareMode ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
              }`}
            >
              {compareMode ? 'Comparison Active' : 'Enable Relative Compare'}
            </button>

            {compareMode && (
              <select
                value={compareStock}
                onChange={(e) => setCompareStock(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-slate-200 font-mono"
              >
                {availableStocks
                  .filter((s) => s !== selectedStock)
                  .map((s) => (
                    <option key={s} value={s}>
                      vs {s}
                    </option>
                  ))}
              </select>
            )}
          </div>
        </div>

        {compareMode && (
          <div className="h-64 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(v) => `${v}%`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                  formatter={(val: any) => [`${val}%`, 'Return']}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey={selectedStock} stroke="#06b6d4" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey={compareStock} stroke="#f59e0b" strokeWidth={2} dot={false} strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};
