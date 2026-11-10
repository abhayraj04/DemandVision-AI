import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Legend
} from 'recharts';
import type { IndicatorDataPoint } from '../types';

interface TechnicalChartProps {
  data: IndicatorDataPoint[];
  symbol: string;
}

export const TechnicalIndicatorsChart: React.FC<TechnicalChartProps> = ({ data, symbol }) => {
  const [subIndicator, setSubIndicator] = useState<'rsi' | 'macd' | 'obv'>('rsi');
  const [showSMA, setShowSMA] = useState(true);
  const [showEMA, setShowEMA] = useState(false);
  const [showBB, setShowBB] = useState(true);

  return (
    <div className="space-y-4">
      {/* Indicator Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-3 rounded-lg border border-terminal-border text-xs font-mono">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400 font-semibold uppercase">Overlays:</span>
          <button
            onClick={() => setShowSMA(!showSMA)}
            className={`px-2.5 py-1 rounded transition border ${
              showSMA ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            SMA (20, 50, 200)
          </button>
          <button
            onClick={() => setShowEMA(!showEMA)}
            className={`px-2.5 py-1 rounded transition border ${
              showEMA ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            EMA (9, 21)
          </button>
          <button
            onClick={() => setShowBB(!showBB)}
            className={`px-2.5 py-1 rounded transition border ${
              showBB ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            Bollinger (20, 2σ)
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-slate-400 font-semibold uppercase">Sub-Pane:</span>
          {(['rsi', 'macd', 'obv'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setSubIndicator(mode)}
              className={`px-2.5 py-1 rounded uppercase font-semibold transition border ${
                subIndicator === mode
                  ? 'bg-blue-600/30 text-blue-300 border-blue-500'
                  : 'bg-slate-800 text-slate-400 border-slate-700'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Main Overlay Price Pane */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3">
        <div className="text-[11px] font-mono text-slate-400 mb-1 flex justify-between">
          <span>{symbol} Price & Overlays</span>
          <span className="text-slate-500">120 Sessions</span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis domain={['auto', 'auto']} stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(v) => `₹${v}`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
              />
              <Line type="monotone" dataKey="close" stroke="#f8fafc" strokeWidth={1.8} dot={false} name="Close" />

              {showSMA && (
                <>
                  <Line type="monotone" dataKey="sma_20" stroke="#f59e0b" strokeWidth={1.2} dot={false} name="SMA 20" />
                  <Line type="monotone" dataKey="sma_50" stroke="#3b82f6" strokeWidth={1.2} dot={false} name="SMA 50" />
                  <Line type="monotone" dataKey="sma_200" stroke="#ec4899" strokeWidth={1.5} dot={false} name="SMA 200" />
                </>
              )}

              {showEMA && (
                <>
                  <Line type="monotone" dataKey="ema_9" stroke="#10b981" strokeWidth={1.2} dot={false} name="EMA 9" />
                  <Line type="monotone" dataKey="ema_21" stroke="#a855f7" strokeWidth={1.2} dot={false} name="EMA 21" />
                </>
              )}

              {showBB && (
                <>
                  <Line type="monotone" dataKey="bb_upper" stroke="#06b6d4" strokeDasharray="2 2" strokeWidth={1} dot={false} name="Upper BB" />
                  <Line type="monotone" dataKey="bb_middle" stroke="#06b6d4" strokeWidth={1} dot={false} name="Middle BB" />
                  <Line type="monotone" dataKey="bb_lower" stroke="#06b6d4" strokeDasharray="2 2" strokeWidth={1} dot={false} name="Lower BB" />
                </>
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sub-Pane: RSI / MACD / OBV */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3">
        <div className="text-[11px] font-mono text-slate-400 mb-1 flex justify-between">
          <span className="uppercase">{subIndicator} Oscillator Panel</span>
          <span className="text-slate-500">Momentum Dynamics</span>
        </div>
        <div className="h-40 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {subIndicator === 'rsi' ? (
              <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 9 }} ticks={[30, 50, 70]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                />
                <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Overbought (70)', fill: '#ef4444', fontSize: 9 }} />
                <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Oversold (30)', fill: '#10b981', fontSize: 9 }} />
                <Line type="monotone" dataKey="rsi_14" stroke="#06b6d4" strokeWidth={1.5} dot={false} name="RSI (14)" />
              </ComposedChart>
            ) : subIndicator === 'macd' ? (
              <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis domain={['auto', 'auto']} stroke="#64748b" tick={{ fontSize: 9 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                />
                <ReferenceLine y={0} stroke="#475569" />
                <Bar dataKey="macd_hist" fill="#3b82f6" name="Histogram" />
                <Line type="monotone" dataKey="macd" stroke="#10b981" strokeWidth={1.3} dot={false} name="MACD" />
                <Line type="monotone" dataKey="macd_signal" stroke="#f59e0b" strokeWidth={1.3} dot={false} name="Signal (9)" />
              </ComposedChart>
            ) : (
              <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
                <YAxis domain={['auto', 'auto']} stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                />
                <Line type="monotone" dataKey="obv" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="OBV" />
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
