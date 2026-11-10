"""
MarketVision AI - Real-Time API Routes & WebSocket Gateway
Exposes streaming quotes, Level-2 Market Depth, intraday timeframes, options chain, and sentiment wire.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.realtime.live_stream import (
    streamer, get_options_chain_analytics, get_live_sentiment_news
)

router = APIRouter(prefix="/api/realtime", tags=["Real-Time Intelligence"])
logger = logging.getLogger(__name__)


@router.get("/quotes")
def get_live_quotes():
    """Returns streaming snapshot of all tracked NSE assets with micro-tick directions."""
    return {
        "market_status": "LIVE_STREAMING_SESSION",
        "ticks": streamer.generate_live_ticks(),
        "tick_count": streamer.tick_count
    }


@router.get("/depth/{symbol}")
def get_market_depth(symbol: str):
    """Returns Level-2 Depth of Market (top 5 bids/asks) and Order Flow Imbalance (OFI)."""
    return streamer.get_level2_market_depth(symbol)


@router.get("/intraday/{symbol}")
def get_intraday_candles(
    symbol: str,
    timeframe: str = Query(default="5M", pattern="^(1M|5M|15M|1H)$", description="Intraday bar resolution"),
    limit: int = Query(default=60, ge=10, le=200, description="Number of intraday bars")
):
    """Returns high-resolution intraday candlestick bars for TradingView rendering."""
    candles = streamer.generate_intraday_candles(symbol, timeframe, limit)
    return {
        "symbol": symbol.upper().replace(".NS", ""),
        "timeframe": timeframe,
        "count": len(candles),
        "data": candles
    }


# Options Analytics Router (Mounted at /api/options)
options_router = APIRouter(prefix="/api/options", tags=["Options & Derivatives Analytics"])

@options_router.get("/chain/{symbol}")
def get_options_chain(symbol: str):
    """Returns NSE Option Chain, Put-Call Ratio (PCR), Max Pain strike, and Black-Scholes Greeks."""
    return get_options_chain_analytics(symbol)


# Sentiment News Wire Router (Mounted at /api/sentiment)
sentiment_router = APIRouter(prefix="/api/sentiment", tags=["Quantitative News & Sentiment"])

@sentiment_router.get("/feed")
def get_sentiment_feed(symbol: Optional[str] = Query(default=None, description="Filter by stock ticker")):
    """Returns institutional real-time financial news wire with NLP sentiment scores and impact ratings."""
    news = get_live_sentiment_news(symbol)
    return {
        "count": len(news),
        "feed": news
    }


# Real-Time WebSocket Gateway
@router.websocket("/ws/ticks")
async def websocket_tick_endpoint(websocket: WebSocket):
    """
    Asynchronous WebSocket streaming live ticks and order book updates every 1.5 seconds.
    Clients connect to ws://localhost:8000/api/realtime/ws/ticks.
    """
    await websocket.accept()
    logger.info("Real-time WebSocket client connected")
    try:
        while True:
            ticks = streamer.generate_live_ticks()
            payload = {
                "type": "TICK_UPDATE",
                "ticks": ticks,
                "server_time": streamer.tick_count
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        logger.info("Real-time WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
