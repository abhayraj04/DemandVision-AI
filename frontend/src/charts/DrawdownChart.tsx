import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

interface DrawdownChartProps {
  data: { date: string; drawdown_pct: number }[];
  symbol: string;
}

export const DrawdownChart: React.FC<DrawdownChartProps> = ({ data, symbol }) => {
  return (
    <div className="w-full h-56 bg-terminal-surface border border-terminal-border rounded-xl p-3">
      <div className="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
        <span className="font-semibold text-slate-200">{symbol} Underwater Drawdown Profile</span>
        <span className="text-[11px] text-slate-500">60-Session Rolling Path</span>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.05} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.4} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(d) => d.slice(5)} />
          <YAxis domain={['auto', 0]} stroke="#64748b" tick={{ fontSize: 9 }} tickFormatter={(v) => `${v}%`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
            formatter={(value: any) => [`${value}%`, 'Drawdown']}
          />
          <Area
            type="monotone"
            dataKey="drawdown_pct"
            stroke="#ef4444"
            strokeWidth={1.5}
            fill="url(#drawdownGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
