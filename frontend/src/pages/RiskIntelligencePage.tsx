import React, { useEffect, useState } from 'react';
import { ShieldAlert, AlertTriangle, PieChart, Activity, Sliders, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';
import type { RiskProfile, PortfolioSimulation } from '../types';
import { DrawdownChart } from '../charts/DrawdownChart';

interface RiskIntelligenceProps {
  selectedStock: string;
  availableStocks: string[];
}

export const RiskIntelligencePage: React.FC<RiskIntelligenceProps> = ({
  selectedStock,
  availableStocks,
}) => {
  const [profile, setProfile] = useState<RiskProfile | null>(null);
  const [definitions, setDefinitions] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  // Portfolio Simulation State
  const [portfolioWeights, setPortfolioWeights] = useState<Record<string, number>>({
    RELIANCE: 25,
    TCS: 25,
    HDFCBANK: 25,
    INFY: 25,
  });
  const [simResult, setSimResult] = useState<PortfolioSimulation | null>(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    async function loadRisk() {
      try {
        setLoading(true);
        const res = await apiService.getStockRisk(selectedStock);
        setProfile(res.profile);
        setDefinitions(res.metric_definitions);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadRisk();
  }, [selectedStock]);

  const handleSimulatePortfolio = async () => {
    try {
      setSimLoading(true);
      const res = await apiService.analyzePortfolio(portfolioWeights);
      setSimResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSimLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!profile) return null;

  const var95 = profile.var_cvar?.['95%'];
  const var99 = profile.var_cvar?.['99%'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-terminal-surface border border-terminal-border p-5 rounded-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <h1 className="text-xl font-bold font-mono text-white">Risk Intelligence: {selectedStock}</h1>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Downside Deviation, Value at Risk (VaR), Extreme Tail Severity & Portfolio Simulation
            </p>
          </div>

          <div className="text-xs font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            Benchmark: <span className="text-market-cyan font-bold">NIFTY 50 Index</span>
          </div>
        </div>
      </div>

      {/* Primary Risk Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 font-mono text-xs">
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Annualized Volatility</span>
          <span className="text-lg font-bold text-white mt-1 block">{profile.annualized_volatility}%</span>
          <span className="text-[10px] text-slate-400">σ × √252</span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Maximum Drawdown</span>
          <span className="text-lg font-bold text-rose-400 mt-1 block">-{profile.max_drawdown_pct}%</span>
          <span className="text-[10px] text-slate-500">Trough: {profile.drawdown_trough_date}</span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Sharpe Ratio</span>
          <span className="text-lg font-bold text-market-green mt-1 block">{profile.sharpe_ratio}</span>
          <span className="text-[10px] text-slate-500">Rf: 6.50% RBI 10Y</span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Sortino Ratio</span>
          <span className="text-lg font-bold text-emerald-300 mt-1 block">{profile.sortino_ratio}</span>
          <span className="text-[10px] text-slate-500">Downside Semi-Dev</span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Beta vs NIFTY 50</span>
          <span className="text-lg font-bold text-cyan-300 mt-1 block">{profile.beta_vs_nifty50}</span>
          <span className="text-[10px] text-slate-400">
            {profile.beta_vs_nifty50 > 1.0 ? 'High Sensitivity' : 'Defensive'}
          </span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-3.5">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Jensen's Alpha</span>
          <span className="text-lg font-bold text-amber-300 mt-1 block">
            {profile.jensens_alpha_pct > 0 ? '+' : ''}
            {profile.jensens_alpha_pct}%
          </span>
          <span className="text-[10px] text-slate-500">Annualized CAPM</span>
        </div>
      </div>

      {/* Drawdown Chart & VaR Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rolling Drawdown Chart */}
        <DrawdownChart data={profile.rolling_drawdowns} symbol={selectedStock} />

        {/* VaR & CVaR Deep Dive */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono text-xs">
          <div className="flex justify-between items-center pb-2 border-b border-terminal-border mb-3">
            <span className="font-bold text-white uppercase text-xs">Value at Risk (VaR) & Tail Loss Matrix</span>
            <span className="text-[10px] text-slate-400">Historical & Cornish-Fisher</span>
          </div>

          <div className="space-y-3">
            {/* 95% Confidence Level */}
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex justify-between font-bold text-slate-200">
                <span>95% Confidence (1 in 20 Days Event)</span>
                <span className="text-cyan-400">1-Day VaR: {var95?.historical_var_1d}%</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
                <div>
                  <span className="text-slate-500 block text-[9px]">HISTORICAL 1D</span>
                  <span className="text-white font-semibold">{var95?.historical_var_1d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">PARAMETRIC 1D</span>
                  <span className="text-white font-semibold">{var95?.parametric_var_1d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">CORNISH-FISHER</span>
                  <span className="text-white font-semibold">{var95?.cornish_fisher_var_1d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">EXPECTED SHORTFALL (CVAR)</span>
                  <span className="text-rose-400 font-bold">{var95?.historical_cvar_1d}%</span>
                </div>
              </div>
            </div>

            {/* 99% Confidence Level */}
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex justify-between font-bold text-slate-200">
                <span>99% Extreme Tail (1 in 100 Days Event)</span>
                <span className="text-rose-400">1-Day VaR: {var99?.historical_var_1d}%</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-400 pt-1 border-t border-slate-800/80">
                <div>
                  <span className="text-slate-500 block text-[9px]">HISTORICAL 1D</span>
                  <span className="text-white font-semibold">{var99?.historical_var_1d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">HISTORICAL 10D</span>
                  <span className="text-white font-semibold">{var99?.historical_var_10d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">CORNISH-FISHER</span>
                  <span className="text-white font-semibold">{var99?.cornish_fisher_var_1d}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[9px]">EXPECTED SHORTFALL (CVAR)</span>
                  <span className="text-rose-400 font-bold">{var99?.historical_cvar_1d}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Multi-Stock Portfolio Risk Simulator */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 font-mono text-xs">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-3 border-b border-terminal-border gap-2 mb-4">
          <div>
            <span className="font-bold text-sm text-white flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-market-cyan" />
              <span>Multi-Asset Portfolio Risk Simulation Sandbox</span>
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              Customize asset weights to measure diversification benefits and portfolio tail risk.
            </span>
          </div>

          <button
            onClick={handleSimulatePortfolio}
            disabled={simLoading}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg transition shadow-md shadow-cyan-500/20 disabled:opacity-50"
          >
            {simLoading ? 'Simulating...' : 'Run Portfolio Simulation'}
          </button>
        </div>

        {/* Weights Sliders */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
          {Object.keys(portfolioWeights).map((sym) => (
            <div key={sym} className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="flex justify-between items-center mb-1">
                <span className="font-bold text-white">{sym}</span>
                <span className="text-cyan-400 font-bold">{portfolioWeights[sym]}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={portfolioWeights[sym]}
                onChange={(e) =>
                  setPortfolioWeights({
                    ...portfolioWeights,
                    [sym]: Number(e.target.value),
                  })
                }
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>
          ))}
        </div>

        {/* Simulation Output */}
        {simResult && (
          <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-800/60 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Expected Return</span>
              <span className="text-base font-bold text-emerald-400 mt-1 block">
                +{simResult.expected_annual_return}%
              </span>
            </div>

            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Portfolio Volatility</span>
              <span className="text-base font-bold text-white mt-1 block">{simResult.annualized_volatility}%</span>
            </div>

            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Diversification Ratio</span>
              <span className="text-base font-bold text-cyan-300 mt-1 block">
                {simResult.diversification_ratio}x
              </span>
            </div>

            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Portfolio Sharpe</span>
              <span className="text-base font-bold text-market-green mt-1 block">{simResult.sharpe_ratio}</span>
            </div>

            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Portfolio Max DD</span>
              <span className="text-base font-bold text-rose-400 mt-1 block">-{simResult.max_drawdown_pct}%</span>
            </div>

            <div>
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Risk Tier</span>
              <span className="text-base font-bold text-amber-300 mt-1 block">{simResult.risk_tier}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
