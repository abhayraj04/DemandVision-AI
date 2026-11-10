import React, { useEffect, useState } from 'react';
import { Trophy, Award, BarChart3, HelpCircle, Layers, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import type { LeaderboardEntry } from '../types';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface ModelPerformanceProps {
  selectedStock: string;
}

export const ModelPerformancePage: React.FC<ModelPerformanceProps> = ({ selectedStock }) => {
  const [leaderboard, setLeaderboard] = useState<Record<string, LeaderboardEntry>>({});
  const [criteria, setCriteria] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPerformance() {
      try {
        setLoading(true);
        const res = await apiService.getModelsPerformance();
        setLeaderboard(res.leaderboard);
        setCriteria(res.evaluation_criteria);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadPerformance();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80">
        <div className="w-8 h-8 border-2 border-market-cyan border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const currentEntry = leaderboard[selectedStock];
  if (!currentEntry) return null;

  return (
    <div className="space-y-6">
      {/* Header and Selection Rationale Banner */}
      <div className="bg-terminal-surface border border-terminal-border p-5 rounded-xl space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <Trophy className="w-5 h-5 text-amber-400" />
              <h1 className="text-xl font-bold font-mono text-white">
                Model Performance Center: {selectedStock}
              </h1>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Comparative Econometric & Machine Learning Leaderboard across Walk-Forward Test Partitions
            </p>
          </div>

          <div className="text-xs font-mono bg-cyan-950/40 border border-cyan-800 text-cyan-300 px-3 py-1.5 rounded-lg flex items-center space-x-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <span>Optimal Model: <strong>{currentEntry.best_model}</strong></span>
          </div>
        </div>

        {/* Model Selection Rationale Callout */}
        <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300">
          <div className="text-cyan-400 font-bold mb-1 flex items-center space-x-1.5">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Institutional Model Selection Principle (Occam's Quantitative Razor)</span>
          </div>
          <p className="leading-relaxed text-slate-400">{currentEntry.selection_rationale}</p>
        </div>
      </div>

      {/* Model Family Leaderboard Table */}
      <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
        <div className="flex justify-between items-center pb-3 border-b border-terminal-border mb-4">
          <span className="font-mono text-xs font-bold text-white uppercase flex items-center space-x-2">
            <Layers className="w-4 h-4 text-market-cyan" />
            <span>Multi-Model Evaluation Leaderboard</span>
          </span>
          <span className="text-[11px] font-mono text-slate-500">Out-of-Sample Performance</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono text-left">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">Model Family</th>
                <th className="py-2.5 px-3">Complexity</th>
                <th className="py-2.5 px-3">RMSE</th>
                <th className="py-2.5 px-3">MAE</th>
                <th className="py-2.5 px-3">MAPE (%)</th>
                <th className="py-2.5 px-3">Directional Accuracy</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3">Rank</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {Object.entries(currentEntry.models).map(([name, m]) => {
                const isBest = name === currentEntry.best_model;
                return (
                  <tr
                    key={name}
                    className={`hover:bg-slate-900/60 transition ${
                      isBest ? 'bg-cyan-950/20 font-semibold' : ''
                    }`}
                  >
                    <td className="py-3 px-3 text-white flex items-center space-x-2">
                      {isBest && <CheckCircle2 className="w-3.5 h-3.5 text-market-cyan shrink-0" />}
                      <span>{name}</span>
                    </td>
                    <td className="py-3 px-3 text-slate-400">{m.model_family}</td>
                    <td className="py-3 px-3 text-slate-500 text-[11px]">{m.complexity}</td>
                    <td className="py-3 px-3 text-cyan-300 font-bold">₹{m.rmse.toFixed(2)}</td>
                    <td className="py-3 px-3 text-slate-300">₹{m.mae.toFixed(2)}</td>
                    <td className="py-3 px-3 text-slate-300">{m.mape.toFixed(2)}%</td>
                    <td className="py-3 px-3 text-emerald-400 font-bold">{m.directional_accuracy.toFixed(1)}%</td>
                    <td className="py-3 px-3 text-slate-400">{m.r2.toFixed(3)}</td>
                    <td className="py-3 px-3">
                      {isBest ? (
                        <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-bold">
                          #1 SELECTED
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

      {/* XGBoost Feature Importance & Residual Statistics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 font-mono text-xs">
        {/* Feature Importance Chart */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5">
          <div className="flex justify-between items-center pb-2 border-b border-terminal-border mb-3">
            <span className="font-bold text-white uppercase">XGBoost Multi-Factor Feature Importance</span>
            <span className="text-[10px] text-slate-500">Gini Gain Weight</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={currentEntry.feature_importances.slice(0, 8)}
                layout="vertical"
                margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 9 }} />
                <YAxis dataKey="feature" type="category" stroke="#94a3b8" tick={{ fontSize: 9 }} width={80} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                  formatter={(val: any) => [`${(val * 100).toFixed(1)}%`, 'Importance']}
                />
                <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Residual Error Diagnostics */}
        <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-terminal-border">
            <span className="font-bold text-white uppercase">Residual Error Distribution (ε = y - ŷ)</span>
            <span className="text-[10px] text-slate-500">Test Partition Diagnostics</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Mean Prediction Error</span>
              <span className="text-base font-bold text-white mt-1 block">
                ₹{currentEntry.residual_stats.mean_error.toFixed(2)}
              </span>
              <span className="text-[10px] text-slate-500">Target: Zero Bias</span>
            </div>

            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Standard Error of Resid.</span>
              <span className="text-base font-bold text-cyan-300 mt-1 block">
                ₹{currentEntry.residual_stats.std_error.toFixed(2)}
              </span>
              <span className="text-[10px] text-slate-500">Residual Dispersion</span>
            </div>

            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Residual Skewness</span>
              <span className="text-base font-bold text-amber-300 mt-1 block">
                {currentEntry.residual_stats.skewness.toFixed(3)}
              </span>
              <span className="text-[10px] text-slate-500">Asymmetry Coefficient</span>
            </div>

            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] uppercase font-semibold block">Excess Kurtosis</span>
              <span className="text-base font-bold text-purple-300 mt-1 block">
                {currentEntry.residual_stats.kurtosis.toFixed(3)}
              </span>
              <span className="text-[10px] text-slate-500">Tail Thickness</span>
            </div>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800/80 rounded-lg text-slate-400 text-[11px] leading-relaxed">
            Residual diagnostics examine whether unmodeled information remains in the forecast errors.
            A near-zero mean confirms the model is unbiased, while low residual skewness indicates balanced error dispersion.
          </div>
        </div>
      </div>
    </div>
  );
};
