import React, { useEffect, useState } from 'react';
import { Newspaper, TrendingUp, TrendingDown, Clock, ShieldCheck } from 'lucide-react';

interface NewsItem {
  id: string;
  symbol: string;
  headline: string;
  source: string;
  time_ago: string;
  sentiment: string;
  score: number;
  impact: string;
  summary: string;
}

interface LiveSentimentFeedProps {
  symbol?: string;
}

export const LiveSentimentFeed: React.FC<LiveSentimentFeedProps> = ({ symbol }) => {
  const [feed, setFeed] = useState<NewsItem[]>([]);

  useEffect(() => {
    async function loadNews() {
      try {
        const url = symbol ? `/api/sentiment/feed?symbol=${symbol}` : '/api/sentiment/feed';
        const res = await fetch(url);
        if (!res.ok) return;
        const data = await res.json();
        setFeed(data.feed);
      } catch (e) {
        console.error(e);
      }
    }
    loadNews();
    const interval = setInterval(loadNews, 8000);
    return () => clearInterval(interval);
  }, [symbol]);

  return (
    <div className="bg-terminal-surface border border-terminal-border rounded-xl p-4 font-mono text-xs space-y-3">
      <div className="flex justify-between items-center pb-2 border-b border-terminal-border">
        <div className="flex items-center space-x-2">
          <Newspaper className="w-4 h-4 text-market-cyan" />
          <span className="font-bold text-white uppercase">Real-Time Market Sentiment Wire</span>
        </div>
        <span className="text-[10px] text-slate-500 flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>Live Algorithmic Scoring</span>
        </span>
      </div>

      <div className="space-y-2.5">
        {feed.map((item) => (
          <div
            key={item.id}
            className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5 hover:border-slate-700 transition"
          >
            <div className="flex items-center justify-between text-[11px]">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-cyan-300">{item.symbol}</span>
                <span className="text-slate-500">|</span>
                <span className="text-slate-400">{item.source}</span>
                <span className="text-slate-600">• {item.time_ago}</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span
                  className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    item.impact === 'HIGH'
                      ? 'bg-purple-950 text-purple-300 border border-purple-800'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {item.impact} IMPACT
                </span>
                <span className="text-[10px] text-emerald-400 font-bold bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-900/60">
                  +{item.score} {item.sentiment}
                </span>
              </div>
            </div>

            <h4 className="font-bold text-white text-xs leading-snug">{item.headline}</h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">{item.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
