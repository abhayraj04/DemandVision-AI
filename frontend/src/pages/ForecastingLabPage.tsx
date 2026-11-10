import React, { useEffect, useState } from 'react';
import { BrainCircuit, Calendar, TrendingUp, TrendingDown, AlertCircle, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import type { ForecastPackage, ForecastHorizon } from '../types';
import { ForecastChart } from '../charts/ForecastChart';

interface ForecastingLabProps {
  selectedStock: string;
}

export const ForecastingLabPage: React.FC<ForecastingLabProps> = ({ selectedStock }) => {
  const [forecastPkg, setForecastPkg] = useState<ForecastPackage | null>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<'7_day' | '14_day' | '30_day'>('14_day');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadForecast() {
      try {
        setLoading(true);
        const pkg = await apiService.getStockForecast(selectedStock);
        setForecastPkg(pkg);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadForecast();
  }, [selectedStock]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!forecastPkg) {
    return (
      <div className="p-6 text-center text-slate-400 font-mono text-xs">
        No forecasting package found for {selectedStock}.
      </div>
    );
  }

  const currentHorizon: ForecastHorizon = forecastPkg.horizons[selectedHorizon];
  const isBull = currentHorizon.projected_direction === 'BULLISH';
  const wfvComp = forecastPkg.walk_forward_validation.comparison;

  return (
    <div className="space-y-6">
      {/* Header and Horizon Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-terminal-surface border border-terminal-border p-5 rounded-xl gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <BrainCircuit className="w-5 h-5 text-market-cyan" />
            <h1 className="text-xl font-bold font-mono text-white">Forecasting Lab: {selectedStock}</h1>
            <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/80 px-2 py-0.5 rounded">
              Walk-Forward Certified
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Statistical Auto-Regressive Projections & Chronological Out-of-Sample Validation
          </p>
        </div>

        {/* Horizon Toggle */}
        <div className="flex items-center space-x-2 bg-slate-900 p-1.5 rounded-lg border border-slate-800 text-xs font-mono">
          <span className="text-slate-500 text-[11px] px-2 uppercase font-semibold">Horizon:</span>
          {(['7_day', '14_day', '30_day'] as const).map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h)}
              className={`px-3 py-1.5 rounded font-bold uppercase transition ${
                selectedHorizon === h
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {h.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Primary Forecast Summary Metrics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Target Forecast Date</span>
          <div className="text-lg font-bold text-white mt-1 flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-market-cyan" />
            <span>{currentHorizon.target_date}</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            {currentHorizon.horizon_days} Trading Days Out
          </span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Current Spot Price</span>
          <div className="text-lg font-bold text-slate-200 mt-1">
            ₹{currentHorizon.current_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Latest NSE Session</span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Projected Target Price</span>
          <div className="text-lg font-bold text-cyan-300 mt-1">
            ₹{currentHorizon.target_predicted_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            95% Range: ₹{currentHorizon.forecast_series[currentHorizon.forecast_series.length - 1]?.lower_bound_95} – ₹{currentHorizon.forecast_series[currentHorizon.forecast_series.length - 1]?.upper_bound_95}
          </span>
        </div>

        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Expected Return & Bias</span>
          <div className={`text-lg font-bold mt-1 flex items-center space-x-1.5 ${isBull ? 'text-market-green' : 'text-market-red'}`}>
            {isBull ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>
              {isBull ? '+' : ''}
              {currentHorizon.expected_return_pct.toFixed(2)}%
            </span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block font-semibold">
            {currentHorizon.projected_direction} Trajectory
          </span>
        </div>
      </div>

      {/* Main Multi-Horizon Forecast Chart with Uncertainty Shading */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-3 border-b border-terminal-border/60 mb-4 gap-2">
          <div>
            <span className="text-xs font-mono font-bold text-white uppercase">
              Actual vs Statistical Forecast Profile ({selectedHorizon.replace('_', ' ')})
            </span>
            <span className="block text-[11px] text-slate-400 font-mono mt-0.5">
              Historical 30-Day Trail with 95% Parametric Error Dispersion Cone
            </span>
          </div>
          <div className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/60 px-2.5 py-1 rounded">
            Best Model: {forecastPkg.walk_forward_validation.best_model}
          </div>
        </div>

        <ForecastChart forecastPackage={forecastPkg} horizonKey={selectedHorizon} />
      </div>

      {/* Out-of-Sample Walk-Forward Validation Table */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
        <div className="flex items-center justify-between pb-3 border-b border-terminal-border mb-4 font-mono">
          <div>
            <span className="text-xs font-bold text-white uppercase flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Out-of-Sample Walk-Forward Validation Benchmark</span>
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              Evaluated on {forecastPkg.walk_forward_validation.validation_horizon}-Day Chronological Test Window (Zero Lookahead)
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono text-left">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">RMSE</th>
                <th className="py-2.5 px-3">MAE</th>
                <th className="py-2.5 px-3">MAPE (%)</th>
                <th className="py-2.5 px-3">Directional Accuracy</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {Object.entries(wfvComp).map(([name, item]) => {
                const isSelected = name === forecastPkg.walk_forward_validation.best_model;
                return (
                  <tr
                    key={name}
                    className={`hover:bg-slate-900/60 transition ${
                      isSelected ? 'bg-cyan-950/20 font-semibold' : ''
                    }`}
                  >
                    <td className="py-3 px-3 text-white flex items-center space-x-2">
                      {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-market-cyan"></span>}
                      <span>{name}</span>
                    </td>
                    <td className="py-3 px-3 text-cyan-300">₹{item.metrics.rmse.toFixed(2)}</td>
                    <td className="py-3 px-3 text-slate-300">₹{item.metrics.mae.toFixed(2)}</td>
                    <td className="py-3 px-3 text-slate-300">{item.metrics.mape.toFixed(2)}%</td>
                    <td className="py-3 px-3 text-emerald-400">{item.metrics.directional_accuracy.toFixed(1)}%</td>
                    <td className="py-3 px-3 text-slate-400">{item.metrics.r2.toFixed(3)}</td>
                    <td className="py-3 px-3">
                      {isSelected ? (
                        <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded font-bold">
                          SELECTED
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500">Benchmark</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Uncertainty Disclaimer Notice */}
      <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-start space-x-3 text-xs font-mono text-slate-400">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-slate-200">Statistical Uncertainty & Educational Boundary: </strong>
          {forecastPkg.uncertainty_disclaimer}
        </p>
      </div>
    </div>
  );
};
