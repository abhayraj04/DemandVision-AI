import React, { useEffect, useState } from 'react';
import { Sparkles, ShieldCheck, TrendingUp, TrendingDown, AlertTriangle, Cpu, Volume2, Target } from 'lucide-react';
import { apiService } from '../services/api';
import type { AIInsights } from '../types';

interface AIInsightsProps {
  selectedStock: string;
}

export const AIInsightsPage: React.FC<AIInsightsProps> = ({ selectedStock }) => {
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInsights() {
      try {
        setLoading(true);
        const res = await apiService.getAIInsights(selectedStock);
        setInsights(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadInsights();
  }, [selectedStock]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!insights) return null;

  const isBull = insights.overall_stance === 'BULLISH_BIAS';
  const isBear = insights.overall_stance === 'BEARISH_BIAS';

  return (
    <div className="space-y-6">
      {/* Header and Verification */}
      <div className="bg-terminal-surface border border-terminal-border p-5 rounded-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-market-cyan" />
              <h1 className="text-xl font-bold font-mono text-white">
                AI Market Intelligence: {insights.company_name} ({insights.symbol})
              </h1>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Deterministic Quantitative Synthesis Engine Grounded in Verified Metrics
            </p>
          </div>

          {/* Stance Badge */}
          <div
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg font-mono text-xs font-bold border uppercase ${
              isBull
                ? 'bg-emerald-950/80 text-emerald-400 border-emerald-800'
                : isBear
                ? 'bg-red-950/80 text-red-400 border-red-800'
                : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            {isBull ? <TrendingUp className="w-4 h-4" /> : isBear ? <TrendingDown className="w-4 h-4" /> : <Cpu className="w-4 h-4" />}
            <span>{insights.overall_stance.replace('_', ' ')}</span>
          </div>
        </div>
      </div>

      {/* Synthesis Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 font-mono">
        {/* Trend & Momentum Summary */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase pb-2 border-b border-terminal-border">
            <TrendingUp className="w-4 h-4" />
            <span>Macro Trend & Moving Average Structure</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">{insights.trend_summary}</p>
        </div>

        {/* Volatility & Extreme Tail Risk */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold uppercase pb-2 border-b border-terminal-border">
            <AlertTriangle className="w-4 h-4" />
            <span>Volatility Dispersion & VaR Observations</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">{insights.volatility_observation}</p>
        </div>

        {/* Unusual Volume Dynamics */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-purple-400 text-xs font-bold uppercase pb-2 border-b border-terminal-border">
            <Volume2 className="w-4 h-4" />
            <span>Institutional Liquidity & Volume Flow</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">{insights.volume_observation}</p>
        </div>

        {/* Risk Warning & CAPM Beta */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase pb-2 border-b border-terminal-border">
            <ShieldCheck className="w-4 h-4" />
            <span>Systematic Risk & Capital Preservation Warning</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">{insights.risk_warning}</p>
        </div>

        {/* Forecast Trajectory & Model Selection Rationale */}
        <div className="md:col-span-2 bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-market-cyan text-xs font-bold uppercase pb-2 border-b border-terminal-border">
            <Target className="w-4 h-4" />
            <span>30-Day Quantitative Trajectory & Econometric Model Rationale</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed pt-1">{insights.forecast_explanation}</p>
        </div>
      </div>

      {/* Zero Hallucination Guarantee Box */}
      <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-start space-x-3 text-xs font-mono text-slate-400">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-200">Factually Grounded & Non-Hallucinatory Architecture: </strong>
          All insights presented above are programmatically derived from deterministic calculations over certified historical NSE data.
          No fabricated statements, synthetic announcements, or speculative financial recommendations are produced.
        </div>
      </div>
    </div>
  );
};
