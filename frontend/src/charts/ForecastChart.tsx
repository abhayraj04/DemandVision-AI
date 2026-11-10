import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import type { ForecastHorizon, ForecastPackage } from '../types';

interface ForecastChartProps {
  forecastPackage: ForecastPackage;
  horizonKey: '7_day' | '14_day' | '30_day';
}

export const ForecastChart: React.FC<ForecastChartProps> = ({
  forecastPackage,
  horizonKey,
}) => {
  const horizon: ForecastHorizon = forecastPackage.horizons[horizonKey];
  const recentHistory = forecastPackage.recent_history.slice(-30);

  // Combine recent history with future forecast
  const chartPoints: any[] = [];

  recentHistory.forEach((h) => {
    chartPoints.push({
      date: h.date,
      actual: h.actual_close,
      predicted: null,
      lower: null,
      upper: null,
      band: null,
    });
  });

  // Link the last actual to forecast for visual continuity
  const lastActual = recentHistory[recentHistory.length - 1];
  if (lastActual) {
    chartPoints[chartPoints.length - 1].predicted = lastActual.actual_close;
  }

  horizon.forecast_series.forEach((f) => {
    chartPoints.push({
      date: f.date,
      actual: null,
      predicted: f.predicted_close,
      lower: f.lower_bound_95,
      upper: f.upper_bound_95,
      band: [f.lower_bound_95, f.upper_bound_95],
    });
  });

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded shadow-xl text-xs font-mono">
          <p className="text-slate-400 mb-1">{label}</p>
          {payload.map((p: any, idx: number) => {
            if (p.value == null) return null;
            return (
              <p key={idx} style={{ color: p.color }} className="flex justify-between space-x-3">
                <span>{p.name}:</span>
                <span className="font-bold">₹{Number(p.value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartPoints} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="uncertaintyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="date"
            stroke="#64748b"
            tick={{ fontSize: 10 }}
            tickFormatter={(val) => val.slice(5)}
          />
          <YAxis
            domain={['auto', 'auto']}
            stroke="#64748b"
            tick={{ fontSize: 10 }}
            tickFormatter={(val) => `₹${val}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
            formatter={(value) => <span className="text-slate-300 font-mono">{value}</span>}
          />

          {/* Historical Actuals */}
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual Historical Close"
            stroke="#94a3b8"
            strokeWidth={2}
            dot={false}
          />

          {/* Forecasted Close */}
          <Line
            type="monotone"
            dataKey="predicted"
            name="Model Projection"
            stroke="#06b6d4"
            strokeWidth={2.5}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: '#06b6d4' }}
          />

          {/* Upper & Lower 95% Confidence Bounds */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="#38bdf8"
            strokeWidth={1}
            strokeOpacity={0.6}
            fill="url(#uncertaintyGradient)"
            name="95% Upper Bound"
          />
          <Area
            type="monotone"
            dataKey="lower"
            stroke="#38bdf8"
            strokeWidth={1}
            strokeOpacity={0.6}
            fill="transparent"
            name="95% Lower Bound"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
