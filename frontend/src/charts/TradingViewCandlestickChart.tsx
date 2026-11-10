import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, HistogramSeries } from 'lightweight-charts';
import type { IChartApi } from 'lightweight-charts';
import type { CandleBar } from '../types';

interface CandlestickChartProps {
  data: CandleBar[];
  height?: number;
  symbol: string;
}

export const TradingViewCandlestickChart: React.FC<CandlestickChartProps> = ({
  data,
  height = 420,
  symbol,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return;

    // Clear previous chart instance
    if (chartRef.current) {
      try {
        chartRef.current.remove();
      } catch (e) {
        console.error(e);
      }
      chartRef.current = null;
    }

    try {
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: '#090d16' },
          textColor: '#94a3b8',
          fontSize: 11,
        },
        grid: {
          vertLines: { color: 'rgba(30, 41, 59, 0.5)' },
          horzLines: { color: 'rgba(30, 41, 59, 0.5)' },
        },
        crosshair: {
          mode: 1,
        },
        rightPriceScale: {
          borderColor: '#1e293b',
        },
        timeScale: {
          borderColor: '#1e293b',
          timeVisible: true,
        },
        width: chartContainerRef.current.clientWidth || 800,
        height: height,
      });

      // lightweight-charts v5 uses chart.addSeries(CandlestickSeries, options)
      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      });

      const formattedData = data.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }));

      candlestickSeries.setData(formattedData as any);

      // Volume series
      const volumeSeries = chart.addSeries(HistogramSeries, {
        color: '#38bdf8',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      });

      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      const formattedVolume = data.map((d) => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)',
      }));

      volumeSeries.setData(formattedVolume as any);

      chart.timeScale().fitContent();
      chartRef.current = chart;

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        }
      };

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        if (chartRef.current) {
          try {
            chartRef.current.remove();
          } catch (e) {
            console.error(e);
          }
          chartRef.current = null;
        }
      };
    } catch (err) {
      console.error('TradingView Candlestick Error:', err);
    }
  }, [data, height, symbol]);

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-terminal-border bg-terminal-surface p-2">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-terminal-border/50 text-xs text-slate-400 font-mono">
        <span className="font-semibold text-slate-200">{symbol} OHLCV Candlestick Feed</span>
        <span className="text-[11px] text-slate-500">TradingView Lightweight Engine v5</span>
      </div>
      <div ref={chartContainerRef} className="w-full" style={{ height }} />
    </div>
  );
};
