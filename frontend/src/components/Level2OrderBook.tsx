import React, { useEffect, useState } from 'react';
import { Layers, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface OrderLevel {
  price: number;
  quantity: number;
  orders: number;
}

interface MarketDepthData {
  symbol: string;
  ltp: number;
  best_bid: number;
  best_ask: number;
  spread: number;
  bids: OrderLevel[];
  asks: OrderLevel[];
  total_buy_quantity: number;
  total_sell_quantity: number;
  buy_pressure_pct: number;
  sell_pressure_pct: number;
  order_flow_imbalance: number;
  imbalance_bias: string;
  timestamp: string;
}

interface Level2OrderBookProps {
  symbol: string;
  liveLtp?: number;
}

export const Level2OrderBook: React.FC<Level2OrderBookProps> = ({ symbol, liveLtp }) => {
  const [depth, setDepth] = useState<MarketDepthData | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchDepth() {
      try {
        const res = await fetch(`/api/realtime/depth/${symbol}`);
        if (!res.ok) return;
        const data = await res.json();
        if (isMounted) setDepth(data);
      } catch (err) {
        console.error(err);
      }
    }

    fetchDepth();
    const interval = setInterval(fetchDepth, 2500);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [symbol]);

  if (!depth) {
    return (
      <div className="p-4 bg-terminal-surface border border-terminal-border rounded-xl font-mono text-xs text-slate-400">
        Loading Level-2 Depth of Market...
      </div>
    );
  }

  const maxQty = Math.max(
    ...depth.bids.map((b) => b.quantity),
    ...depth.asks.map((a) => a.quantity),
    1
  );

  return (
    <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono text-xs space-y-3">
      {/* Header */}
      <div className="flex justify-between items-center pb-2 border-b border-terminal-border">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-market-cyan" />
          <span className="font-bold text-white uppercase">Level-2 Depth of Market (DOM)</span>
        </div>
        <div className="flex items-center space-x-2 text-[11px]">
          <span className="text-slate-400">Spread:</span>
          <span className="text-cyan-300 font-bold">₹{depth.spread}</span>
        </div>
      </div>

      {/* Buy / Sell Pressure Imbalance Bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-[11px] font-bold">
          <span className="text-emerald-400 flex items-center space-x-1">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>BUY {depth.buy_pressure_pct}%</span>
          </span>
          <span className="text-slate-400 text-[10px] uppercase">{depth.imbalance_bias.replace(/_/g, ' ')}</span>
          <span className="text-rose-400 flex items-center space-x-1">
            <span>SELL {depth.sell_pressure_pct}%</span>
            <ArrowDownRight className="w-3.5 h-3.5" />
          </span>
        </div>
        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden flex">
          <div
            className="h-full bg-emerald-500 transition-all duration-500"
            style={{ width: `${depth.buy_pressure_pct}%` }}
          />
          <div
            className="h-full bg-rose-500 transition-all duration-500"
            style={{ width: `${depth.sell_pressure_pct}%` }}
          />
        </div>
      </div>

      {/* 5-Level Bid / Ask Grid */}
      <div className="grid grid-cols-2 gap-3 pt-1">
        {/* BIDS (Buyers) */}
        <div>
          <div className="flex justify-between text-[10px] text-slate-500 uppercase pb-1 border-b border-slate-800">
            <span>Orders</span>
            <span>Qty</span>
            <span>Bid Price</span>
          </div>
          <div className="divide-y divide-slate-800/40">
            {depth.bids.map((b, i) => (
              <div key={i} className="flex justify-between items-center py-1 text-[11px] relative">
                <div
                  className="absolute left-0 top-0 bottom-0 bg-emerald-500/10 pointer-events-none"
                  style={{ width: `${(b.quantity / maxQty) * 100}%` }}
                />
                <span className="text-slate-500 z-10">{b.orders}</span>
                <span className="text-slate-300 z-10 font-bold">{b.quantity.toLocaleString('en-IN')}</span>
                <span className="text-emerald-400 font-bold z-10">₹{b.price.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between pt-1 text-[10px] text-slate-400 border-t border-slate-800">
            <span>Total Buy Qty:</span>
            <span className="text-emerald-400 font-bold">{depth.total_buy_quantity.toLocaleString('en-IN')}</span>
          </div>
        </div>

        {/* ASKS (Sellers) */}
        <div>
          <div className="flex justify-between text-[10px] text-slate-500 uppercase pb-1 border-b border-slate-800">
            <span>Ask Price</span>
            <span>Qty</span>
            <span>Orders</span>
          </div>
          <div className="divide-y divide-slate-800/40">
            {depth.asks.map((a, i) => (
              <div key={i} className="flex justify-between items-center py-1 text-[11px] relative">
                <div
                  className="absolute right-0 top-0 bottom-0 bg-rose-500/10 pointer-events-none"
                  style={{ width: `${(a.quantity / maxQty) * 100}%` }}
                />
                <span className="text-rose-400 font-bold z-10">₹{a.price.toFixed(2)}</span>
                <span className="text-slate-300 z-10 font-bold">{a.quantity.toLocaleString('en-IN')}</span>
                <span className="text-slate-500 z-10">{a.orders}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between pt-1 text-[10px] text-slate-400 border-t border-slate-800">
            <span>Total Sell Qty:</span>
            <span className="text-rose-400 font-bold">{depth.total_sell_quantity.toLocaleString('en-IN')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
