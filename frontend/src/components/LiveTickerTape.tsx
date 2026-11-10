import React from 'react';
import { TrendingUp, TrendingDown, Radio } from 'lucide-react';
import type { LiveTick } from '../hooks/useRealtimeStream';

interface LiveTickerTapeProps {
  ticks: Record<string, LiveTick>;
  onSelectStock: (symbol: string) => void;
  selectedStock: string;
}

export const LiveTickerTape: React.FC<LiveTickerTapeProps> = ({
  ticks,
  onSelectStock,
  selectedStock,
}) => {
  const displaySymbols = ['NIFTY_50', 'NIFTY_BANK', 'NIFTY_IT', 'INDIA_VIX', 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'ITC', 'BHARTIARTL'];

  return (
    <div className="bg-slate-950/90 border-b border-terminal-border/80 px-4 py-2 flex items-center overflow-x-auto space-x-6 text-xs font-mono scrollbar-none sticky top-16 z-30 backdrop-blur-md">
      <div className="flex items-center space-x-1.5 text-[10px] text-emerald-400 font-bold tracking-wider uppercase shrink-0 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-900/60">
        <Radio className="w-3 h-3 animate-pulse" />
        <span>Live Stream</span>
      </div>

      {displaySymbols.map((sym) => {
        const tick = ticks[sym];
        if (!tick) return null;
        const isPos = tick.pct_change >= 0;
        const isSelected = sym === selectedStock;

        // Flash background micro-animation
        const flashClass =
          tick.flash === 'up'
            ? 'bg-emerald-500/20 text-emerald-300'
            : tick.flash === 'down'
            ? 'bg-rose-500/20 text-rose-300'
            : '';

        return (
          <button
            key={sym}
            onClick={() => onSelectStock(sym.replace('_', ' '))}
            className={`flex items-center space-x-2 shrink-0 px-2 py-1 rounded transition duration-300 ${flashClass} ${
              isSelected ? 'bg-slate-800 border border-slate-700' : 'hover:bg-slate-900'
            }`}
          >
            <span className="text-slate-400 font-semibold">{sym.replace('_', ' ')}:</span>
            <span className="text-white font-bold">
              ₹{tick.ltp.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </span>
            <span
              className={`flex items-center space-x-0.5 text-[11px] font-bold ${
                isPos ? 'text-market-green' : 'text-market-red'
              }`}
            >
              {isPos ? <TrendingUp className="w-3 h-3 inline" /> : <TrendingDown className="w-3 h-3 inline" />}
              <span>
                {isPos ? '+' : ''}
                {tick.pct_change.toFixed(2)}%
              </span>
            </span>
          </button>
        );
      })}
    </div>
  );
};
