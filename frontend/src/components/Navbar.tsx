import React from 'react';
import { Search, Activity, ShieldCheck, Clock } from 'lucide-react';

interface NavbarProps {
  selectedStock: string;
  onSelectStock: (symbol: string) => void;
  availableStocks: string[];
}

export const Navbar: React.FC<NavbarProps> = ({
  selectedStock,
  onSelectStock,
  availableStocks,
}) => {
  return (
    <header className="h-16 border-b border-terminal-border bg-terminal-surface/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Market Status */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-mono font-bold text-white text-lg shadow-lg shadow-cyan-500/20">
            M
          </div>
          <div>
            <span className="font-bold tracking-tight text-white font-mono text-base">
              Market<span className="text-market-cyan">Vision</span> <span className="text-xs px-1.5 py-0.5 rounded bg-blue-950 border border-blue-800 text-blue-300 ml-1">AI</span>
            </span>
            <span className="block text-[10px] text-slate-400 font-mono tracking-widest uppercase">
              NSE Quantitative Terminal
            </span>
          </div>
        </div>

        {/* Market Status Pill */}
        <div className="hidden md:flex items-center space-x-2 bg-slate-900/80 px-3 py-1 rounded-full border border-slate-800 text-xs">
          <span className="w-2 h-2 rounded-full bg-market-amber animate-pulse"></span>
          <span className="text-slate-300 font-mono text-[11px]">NSE Session (Historical Research Mode)</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400 text-[11px] flex items-center space-x-1">
            <Clock className="w-3 h-3 text-slate-400 inline" />
            <span>IST 09:15–15:30</span>
          </span>
        </div>
      </div>

      {/* Global Stock Search & Active Ticker */}
      <div className="flex items-center space-x-4">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <select
            value={selectedStock}
            onChange={(e) => onSelectStock(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-lg pl-9 pr-8 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-market-cyan appearance-none cursor-pointer hover:border-slate-600 transition"
          >
            {availableStocks.map((sym) => (
              <option key={sym} value={sym}>
                {sym}.NS
              </option>
            ))}
          </select>
        </div>

        {/* Institutional Badge */}
        <div className="hidden lg:flex items-center space-x-1.5 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-900/60 px-2.5 py-1 rounded">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Walk-Forward Certified</span>
        </div>
      </div>
    </header>
  );
};
