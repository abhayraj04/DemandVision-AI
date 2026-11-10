import React, { useEffect, useState } from 'react';
import { LineChart, BookOpen, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';
import { apiService } from '../services/api';
import type { IndicatorDataPoint, AnalyticalSignal } from '../types';
import { TechnicalIndicatorsChart } from '../charts/TechnicalIndicatorsChart';

interface TechnicalLabProps {
  selectedStock: string;
}

export const TechnicalLabPage: React.FC<TechnicalLabProps> = ({ selectedStock }) => {
  const [data, setData] = useState<IndicatorDataPoint[]>([]);
  const [signals, setSignals] = useState<AnalyticalSignal[]>([]);
  const [catalog, setCatalog] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [activeCatalogItem, setActiveCatalogItem] = useState<string>('RSI');

  useEffect(() => {
    async function loadIndicators() {
      try {
        setLoading(true);
        const res = await apiService.getStockIndicators(selectedStock, 140);
        setData(res.history);
        setSignals(res.active_signals);
        setCatalog(res.indicator_catalog);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadIndicators();
  }, [selectedStock]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Non-Advisory Notice */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-slate-900 border border-terminal-border p-4 rounded-xl gap-3">
        <div>
          <h1 className="text-xl font-bold font-mono text-white flex items-center space-x-2">
            <LineChart className="w-5 h-5 text-market-cyan" />
            <span>Technical Analysis Lab: {selectedStock}</span>
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Institutional Quantitative Overlays, Dynamic Oscillators & Algorithmic Signals
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-amber-400 bg-amber-950/40 border border-amber-900/50 px-3 py-1.5 rounded-lg">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>Analytical Signals Only — Non-Advisory Research</span>
        </div>
      </div>

      {/* Main Technical Chart */}
      <TechnicalIndicatorsChart data={data} symbol={selectedStock} />

      {/* Analytical Signals & Indicator Educational Catalog Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Analytical Signals */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
          <div className="flex items-center justify-between pb-3 border-b border-terminal-border mb-4">
            <span className="text-xs font-mono font-bold text-white uppercase flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Current Technical Conditions ({signals.length})</span>
            </span>
            <span className="text-[11px] font-mono text-slate-500">Evaluated on Latest Bar</span>
          </div>

          <div className="space-y-3">
            {signals.map((s, idx) => {
              const isBull = s.bias === 'BULLISH_BIAS';
              const isBear = s.bias === 'BEARISH_BIAS';
              return (
                <div
                  key={idx}
                  className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800/80 space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-slate-200">{s.indicator}</span>
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase ${
                        isBull
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : isBear
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {s.condition}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono leading-relaxed">{s.detail}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Educational Indicator Reference */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
          <div className="flex items-center justify-between pb-3 border-b border-terminal-border mb-4">
            <span className="text-xs font-mono font-bold text-white uppercase flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-market-cyan" />
              <span>Indicator Educational Reference</span>
            </span>
            <span className="text-[11px] font-mono text-slate-500">Formulas & Logic</span>
          </div>

          {/* Quick Tabs */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {Object.keys(catalog).map((name) => (
              <button
                key={name}
                onClick={() => setActiveCatalogItem(name)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition border ${
                  activeCatalogItem === name
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 font-bold'
                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                }`}
              >
                {name}
              </button>
            ))}
          </div>

          {catalog[activeCatalogItem] && (
            <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 space-y-3 font-mono text-xs">
              <div className="font-bold text-sm text-cyan-400">{catalog[activeCatalogItem].name}</div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-semibold">Mathematical Formula</span>
                <code className="text-market-green bg-slate-950 px-2 py-1 rounded block mt-1 overflow-x-auto">
                  {catalog[activeCatalogItem].formula}
                </code>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-semibold">Institutional Interpretation</span>
                <p className="text-slate-300 mt-1 leading-relaxed">{catalog[activeCatalogItem].interpretation}</p>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-semibold">Signal Trigger Criteria</span>
                <p className="text-slate-400 mt-1 leading-relaxed">{catalog[activeCatalogItem].signals}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
