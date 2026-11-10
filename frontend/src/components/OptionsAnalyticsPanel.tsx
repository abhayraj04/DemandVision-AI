import React, { useEffect, useState } from 'react';
import { Target, Activity, Zap, TrendingUp, TrendingDown, HelpCircle } from 'lucide-react';

interface OptionStrike {
  strike: number;
  call_ltp: number;
  call_oi: number;
  call_delta: number;
  put_ltp: number;
  put_oi: number;
  put_delta: number;
  is_atm: boolean;
}

interface OptionsChainData {
  symbol: string;
  spot_price: number;
  atm_strike: number;
  implied_volatility_pct: number;
  days_to_expiry: number;
  put_call_ratio: number;
  pcr_sentiment: string;
  max_pain_strike: number;
  total_call_open_interest: number;
  total_put_open_interest: number;
  atm_greeks: {
    call_delta: number;
    put_delta: number;
    gamma: number;
    theta_daily: number;
    vega_per_pct: number;
  };
  option_chain: OptionStrike[];
}

interface OptionsAnalyticsProps {
  symbol: string;
}

export const OptionsAnalyticsPanel: React.FC<OptionsAnalyticsProps> = ({ symbol }) => {
  const [data, setData] = useState<OptionsChainData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOptions() {
      try {
        setLoading(true);
        const res = await fetch(`/api/options/chain/${symbol}`);
        if (!res.ok) return;
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadOptions();
  }, [symbol]);

  if (loading) {
    return (
      <div className="p-5 bg-terminal-surface border border-terminal-border rounded-xl font-mono text-xs text-slate-400">
        Loading Option Chain & Greeks...
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-terminal-surface border border-terminal-border rounded-xl p-5 font-mono text-xs space-y-4">
      {/* Title & Expiry */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-3 border-b border-terminal-border gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white uppercase">{symbol} Derivatives & Option Chain Analytics</h3>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5">
            NSE Monthly Contract | {data.days_to_expiry} Days to Expiry | Implied Volatility: {data.implied_volatility_pct}%
          </p>
        </div>

        {/* PCR Sentiment Badge */}
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
          <span className="text-slate-400">PCR:</span>
          <span className="text-cyan-400 font-bold text-sm">{data.put_call_ratio}</span>
          <span
            className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
              data.put_call_ratio > 1.2
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                : data.put_call_ratio < 0.8
                ? 'bg-rose-950 text-rose-300 border border-rose-800'
                : 'bg-slate-800 text-slate-300 border border-slate-700'
            }`}
          >
            {data.pcr_sentiment.replace(/_/g, ' ')}
          </span>
        </div>
      </div>

      {/* Greeks and Max Pain Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Max Pain Level</span>
          <span className="text-base font-bold text-cyan-300 mt-1 block">₹{data.max_pain_strike}</span>
          <span className="text-[10px] text-slate-500">Least Writer Loss</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">ATM Call Delta (Δ)</span>
          <span className="text-base font-bold text-emerald-400 mt-1 block">+{data.atm_greeks.call_delta}</span>
          <span className="text-[10px] text-slate-500">Price Sensitivity</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">ATM Put Delta (Δ)</span>
          <span className="text-base font-bold text-rose-400 mt-1 block">{data.atm_greeks.put_delta}</span>
          <span className="text-[10px] text-slate-500">Hedge Ratio</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Gamma (Γ)</span>
          <span className="text-base font-bold text-white mt-1 block">{data.atm_greeks.gamma}</span>
          <span className="text-[10px] text-slate-500">Delta Curvature</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Theta (Θ Daily)</span>
          <span className="text-base font-bold text-rose-400 mt-1 block">₹{data.atm_greeks.theta_daily}</span>
          <span className="text-[10px] text-slate-500">Time Decay/Day</span>
        </div>

        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-slate-500 text-[10px] uppercase font-semibold block">Vega (V per 1% IV)</span>
          <span className="text-base font-bold text-purple-400 mt-1 block">₹{data.atm_greeks.vega_per_pct}</span>
          <span className="text-[10px] text-slate-500">Vol Sensitivity</span>
        </div>
      </div>

      {/* Option Chain Strike Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-center text-xs">
          <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
            <tr>
              <th className="py-2 px-3 text-emerald-400" colSpan={3}>CALLS (Bullish Flow)</th>
              <th className="py-2 px-3 bg-slate-950 text-white font-bold">STRIKE</th>
              <th className="py-2 px-3 text-rose-400" colSpan={3}>PUTS (Hedging Flow)</th>
            </tr>
            <tr className="border-t border-slate-800/60 text-[9px] text-slate-500">
              <th className="py-1 px-2">Delta</th>
              <th className="py-1 px-2">Call LTP</th>
              <th className="py-1 px-2">Call OI</th>
              <th className="py-1 px-2 bg-slate-950 text-slate-400">Price</th>
              <th className="py-1 px-2">Put OI</th>
              <th className="py-1 px-2">Put LTP</th>
              <th className="py-1 px-2">Delta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {data.option_chain.map((c) => (
              <tr
                key={c.strike}
                className={`hover:bg-slate-900/60 transition ${
                  c.is_atm ? 'bg-cyan-950/30 font-bold border-y border-cyan-800/60' : ''
                }`}
              >
                <td className="py-2 px-2 text-slate-400">+{c.call_delta}</td>
                <td className="py-2 px-2 text-emerald-400 font-semibold">₹{c.call_ltp}</td>
                <td className="py-2 px-2 text-slate-300">{c.call_oi.toLocaleString('en-IN')}</td>
                <td className="py-2 px-2 bg-slate-950 text-white font-bold">
                  ₹{c.strike} {c.is_atm && <span className="text-[9px] text-cyan-400 ml-1">ATM</span>}
                </td>
                <td className="py-2 px-2 text-slate-300">{c.put_oi.toLocaleString('en-IN')}</td>
                <td className="py-2 px-2 text-rose-400 font-semibold">₹{c.put_ltp}</td>
                <td className="py-2 px-2 text-slate-400">{c.put_delta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
