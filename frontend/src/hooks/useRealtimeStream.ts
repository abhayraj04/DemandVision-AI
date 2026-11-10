import { useState, useEffect, useRef } from 'react';

export interface LiveTick {
  symbol: string;
  ltp: number;
  change: number;
  pct_change: number;
  open: number;
  high: number;
  low: number;
  prev_close: number;
  volume: number;
  tick_direction: 'UP' | 'DOWN';
  timestamp: string;
  flash?: 'up' | 'down' | null;
}

export function useRealtimeStream(intervalMs: number = 2000, isPaused: boolean = false) {
  const [ticks, setTicks] = useState<Record<string, LiveTick>>({});
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [lastTickTime, setLastTickTime] = useState<string>('');
  const prevTicksRef = useRef<Record<string, LiveTick>>({});

  useEffect(() => {
    if (isPaused) return;

    let isMounted = true;

    async function pollQuotes() {
      try {
        const res = await fetch('/api/realtime/quotes');
        if (!res.ok) throw new Error('Live quotes fetch failed');
        const data = await res.json();
        
        if (!isMounted) return;

        const updatedTicks: Record<string, LiveTick> = {};
        const prev = prevTicksRef.current;

        Object.entries(data.ticks).forEach(([sym, tickObj]: [string, any]) => {
          const oldLtp = prev[sym]?.ltp;
          let flash: 'up' | 'down' | null = null;
          if (oldLtp !== undefined) {
            if (tickObj.ltp > oldLtp) flash = 'up';
            else if (tickObj.ltp < oldLtp) flash = 'down';
          }

          updatedTicks[sym] = {
            ...tickObj,
            flash,
          };
        });

        prevTicksRef.current = updatedTicks;
        setTicks(updatedTicks);
        setIsConnected(true);
        setLastTickTime(new Date().toLocaleTimeString('en-IN', { hour12: false }));
      } catch (err) {
        if (isMounted) setIsConnected(false);
      }
    }

    // Initial poll
    pollQuotes();

    const interval = setInterval(pollQuotes, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [intervalMs, isPaused]);

  return { ticks, isConnected, lastTickTime };
}
