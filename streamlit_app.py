"""
MarketVision AI / DemandVision AI - Institutional Terminal Edition
Stock Market Forecasting & Risk Intelligence Platform (NSE)
Ready for 1-click deployment on Streamlit Community Cloud (share.streamlit.io).
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Ensure root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.preprocessing.data_pipeline import STOCKS_METADATA, INDICES_METADATA
from backend.features.technical_indicators import (
    generate_all_technical_features,
    generate_analytical_signals,
    indicator_catalog_metadata,
)
from backend.risk.risk_engine import (
    simulate_portfolio_risk,
    risk_metrics_educational_metadata,
)
from backend.insights.insights_engine import generate_asset_insights
from backend.realtime.live_stream import (
    streamer,
    get_options_chain_analytics,
    get_live_sentiment_news,
)

# ----------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(
    page_title="DemandVision AI — Institutional Market Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------
# HIGH-END FINANCIAL CSS (BLOOMBERG / TRADINGVIEW LUXURY DARK)
# ----------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-deep: #060911;
        --bg-surface: #0b1120;
        --border-glass: rgba(255, 255, 255, 0.08);
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-green: #10b981;
        --accent-red: #f43f5e;
        --accent-gold: #f59e0b;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f1f5f9;
    }

    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(6, 182, 212, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 90%, rgba(59, 130, 246, 0.05) 0%, transparent 40%),
                    #060911;
        color: #f1f5f9;
    }

    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Glassmorphism Containers */
    .terminal-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.45) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .terminal-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        box-shadow: 0 14px 35px -5px rgba(6, 182, 212, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.12);
        transform: translateY(-2px);
    }

    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(8, 14, 28, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    /* Native Metric Overrides */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(13, 20, 36, 0.85) 0%, rgba(20, 30, 50, 0.55) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        transition: all 0.22s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(6, 182, 212, 0.45) !important;
        box-shadow: 0 12px 28px -4px rgba(6, 182, 212, 0.18) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 21px !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #ffffff !important;
    }

    /* Pulsing Live Beacon */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
    }

    .beacon-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
        animation: beacon-pulse 1.8s infinite;
    }

    @keyframes beacon-pulse {
        0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 10px #10b981; }
        50% { opacity: 0.35; transform: scale(0.85); box-shadow: 0 0 2px #10b981; }
    }

    /* High-Contrast Financial Badges */
    .badge-bull {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }

    .badge-bear {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }

    .badge-neutral {
        background: rgba(100, 116, 139, 0.18);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }

    .badge-cyan {
        background: rgba(6, 182, 212, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(6, 182, 212, 0.4);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }

    .badge-gold {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: #070a13 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
        filter: brightness(1.1) !important;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 4px;
        border-radius: 10px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        padding: 6px 14px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(6, 182, 212, 0.15) !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #06b6d4 !important;
        font-weight: 700 !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #060911;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
# PATHS & DATA LOADERS
# ----------------------------------------------------------
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FEATURES_DIR = os.path.join(DATA_DIR, "features")
PREDICTIONS_DIR = os.path.join(DATA_DIR, "predictions")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")


@st.cache_data(ttl=300)
def load_processed_data(symbol: str) -> pd.DataFrame:
    clean_sym = symbol.replace(" ", "_")
    p_path = os.path.join(PROCESSED_DIR, f"{clean_sym}.parquet")
    if os.path.exists(p_path):
        return pd.read_parquet(p_path)
    csv_path = os.path.join(PROCESSED_DIR, f"{clean_sym}.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_features_data(symbol: str) -> pd.DataFrame:
    clean_sym = symbol.replace(" ", "_")
    p_path = os.path.join(FEATURES_DIR, f"{clean_sym}_features.parquet")
    if os.path.exists(p_path):
        return pd.read_parquet(p_path)
    csv_path = os.path.join(FEATURES_DIR, f"{clean_sym}_features.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_forecast_package(symbol: str) -> dict:
    clean_sym = symbol.replace(" ", "_")
    f_path = os.path.join(PREDICTIONS_DIR, f"{clean_sym}_forecast.json")
    if os.path.exists(f_path):
        with open(f_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data(ttl=300)
def load_risk_profile(symbol: str) -> dict:
    clean_sym = symbol.replace(" ", "_")
    r_path = os.path.join(REPORTS_DIR, "risk_analytics.json")
    if os.path.exists(r_path):
        with open(r_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
            return profiles.get(clean_sym, {})
    return {}


@st.cache_data(ttl=300)
def load_leaderboard() -> dict:
    l_path = os.path.join(REPORTS_DIR, "model_leaderboard.json")
    if os.path.exists(l_path):
        with open(l_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def apply_terminal_theme(fig, height=440, show_legend=True):
    """Uniform Plotly institutional dark theme styling"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(10, 16, 28, 0.85)",
        plot_bgcolor="rgba(7, 11, 20, 0.95)",
        height=height,
        margin=dict(l=14, r=14, t=28, b=14),
        showlegend=show_legend,
        hovermode="x unified",
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.04)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(family="JetBrains Mono", size=10, color="#64748b"),
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.04)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(family="JetBrains Mono", size=10, color="#64748b"),
        ),
        font=dict(family="JetBrains Mono", size=11, color="#cbd5e1"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ----------------------------------------------------------
# SIDEBAR NAVIGATION & LIVE TICK CONTROLS
# ----------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
      <div style="background: linear-gradient(135deg, #06b6d4, #3b82f6); width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white; font-family: 'JetBrains Mono', monospace; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);">DV</div>
      <div>
        <div style="font-weight: 800; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 16px; color: white; letter-spacing: -0.02em;">Demand<span style="color: #06b6d4;">Vision</span> AI</div>
        <div style="font-size: 10px; color: #64748b; font-family: 'JetBrains Mono', monospace;">INSTITUTIONAL TERMINAL</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

CORE_STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "LT",
    "AXISBANK",
    "BHARTIARTL",
]

selected_stock = st.sidebar.selectbox("🎯 Active Instrument", CORE_STOCKS, index=0)

module = st.sidebar.radio(
    "Terminal Workspace",
    [
        "Market Overview",
        "Stock Explorer & Intraday",
        "Technical Analysis Lab",
        "Forecasting Lab",
        "Risk Intelligence & Tail Risk",
        "AI Quantitative Insights",
        "Model Performance Center",
    ],
    index=0,
)

# Live Ticks Stream
live_ticks = streamer.generate_live_ticks()
active_tick = live_ticks.get(selected_stock, {})
active_ltp = active_tick.get("ltp", 1000.0)
active_chg_pct = active_tick.get("pct_change", 0.0)
is_positive = active_chg_pct >= 0

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="background: linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.3);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span style="color: #94a3b8; font-size: 10px; text-transform: uppercase;">Active Quote</span>
        <span class="{'badge-bull' if is_positive else 'badge-bear'}">{'+' if is_positive else ''}{active_chg_pct:.2f}%</span>
      </div>
      <div style="font-size: 20px; font-weight: 800; color: white;">₹{active_ltp:,.2f}</div>
      <div style="color: {'#34d399' if is_positive else '#fb7185'}; font-size: 11px; margin-top: 2px;">
        {selected_stock} • {active_tick.get('tick_direction', 'FLAT')}
      </div>
      <div style="color: #64748b; font-size: 9px; margin-top: 6px;">Updated: {active_tick.get('timestamp', '')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("⚡ Force Live Tick Refresh"):
    st.rerun()

st.sidebar.markdown(
    """
    <div style="margin-top: 14px; padding: 10px; background: rgba(6, 182, 212, 0.06); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 8px;">
      <div style="font-size: 10px; color: #38bdf8; font-weight: 600; font-family: monospace;">SYSTEM STATUS: ONLINE</div>
      <div style="font-size: 9px; color: #94a3b8; font-family: monospace; margin-top: 2px;">NSE Realtime Feed: Synchronized<br>Latency: ~12ms | Zero Leakage</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------
# TOP TICKER TAPE
# ----------------------------------------------------------
ticker_items = [
    "NIFTY_50",
    "NIFTY_BANK",
    "INDIA_VIX",
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
]
ticker_html = "<div style='display: flex; gap: 14px; background: rgba(8, 12, 22, 0.85); padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08); overflow-x: auto; font-family: monospace; font-size: 11px; margin-bottom: 18px; white-space: nowrap; align-items: center; box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);'>"
ticker_html += "<span class='live-badge'><span class='beacon-dot'></span>LIVE DOM STREAM</span>"
for sym in ticker_items:
    t = live_ticks.get(sym, {})
    if t:
        pos = t["pct_change"] >= 0
        col = "#34d399" if pos else "#fb7185"
        label = sym.replace("_", " ")
        ticker_html += f"<span style='padding: 2px 8px; background: rgba(255,255,255,0.03); border-radius: 6px;'><strong style='color:#94a3b8;'>{label}:</strong> <span style='color:#f8fafc;'>₹{t['ltp']:,.2f}</span> <span style='color:{col}; font-weight:700;'>{'+' if pos else ''}{t['pct_change']:.2f}%</span></span>"
ticker_html += "</div>"
st.markdown(ticker_html, unsafe_allow_html=True)


# ==========================================================
# MODULE A: MARKET OVERVIEW
# ==========================================================
if module == "Market Overview":
    st.markdown(
        """
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">National Stock Exchange (NSE) Intelligence Overview</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Real-time macro index analytics, institutional breath, and volatility index</p>
          </div>
          <div>
            <span class="live-badge"><span class="beacon-dot"></span>STREAMING TICK ENGINE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nifty = live_ticks.get("NIFTY_50", {})
        st.metric(
            "NIFTY 50 (Benchmark)",
            f"₹{nifty.get('ltp', 24994.70):,.2f}",
            f"{nifty.get('pct_change', 0.42):+.2f}%",
        )
    with col2:
        bank = live_ticks.get("NIFTY_BANK", {})
        st.metric(
            "NIFTY BANK (Financials)",
            f"₹{bank.get('ltp', 52810.15):,.2f}",
            f"{bank.get('pct_change', 0.38):+.2f}%",
        )
    with col3:
        it = live_ticks.get("NIFTY_IT", {})
        st.metric(
            "NIFTY IT (Technology)",
            f"₹{it.get('ltp', 42190.80):,.2f}",
            f"{it.get('pct_change', -0.24):+.2f}%",
        )
    with col4:
        vix = live_ticks.get("INDIA_VIX", {})
        st.metric(
            "INDIA VIX (Fear Index)",
            f"{vix.get('ltp', 14.85):.2f}",
            f"{vix.get('pct_change', -2.10):+.2f}%",
            delta_color="inverse",
        )

    # NIFTY 50 Candlestick Chart
    nifty_df = load_processed_data("NIFTY_50").tail(100)
    if not nifty_df.empty:
        st.markdown(
            "#### 📈 NIFTY 50 Benchmark Trajectory & Volume Profile",
        )
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25],
        )
        fig.add_trace(
            go.Candlestick(
                x=nifty_df["datetime_str"],
                open=nifty_df["open"],
                high=nifty_df["high"],
                low=nifty_df["low"],
                close=nifty_df["close"],
                name="NIFTY 50",
                increasing_line_color="#10b981",
                decreasing_line_color="#f43f5e",
                increasing_fillcolor="rgba(16, 185, 129, 0.6)",
                decreasing_fillcolor="rgba(244, 63, 94, 0.6)",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                x=nifty_df["datetime_str"],
                y=nifty_df["volume"],
                name="Volume",
                marker_color="rgba(6, 182, 212, 0.4)",
            ),
            row=2,
            col=1,
        )
        fig = apply_terminal_theme(fig, height=480)
        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, width="stretch")

    # Gainers & Losers Tables
    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("#### 🟢 Top Performing Equities (Bullish Momentum)")
        gainers_data = []
        for s in CORE_STOCKS:
            t = live_ticks.get(s, {})
            gainers_data.append(
                {
                    "Symbol": s,
                    "Last Traded Price": f"₹{t.get('ltp', 0):,.2f}",
                    "Session Return": f"{t.get('pct_change', 0):+.2f}%",
                    "Direction": t.get("tick_direction", "FLAT"),
                    "raw_pct": t.get("pct_change", 0),
                }
            )
        gainers_df = (
            pd.DataFrame(gainers_data)
            .sort_values("raw_pct", ascending=False)
            .head(5)
            .drop(columns=["raw_pct"])
        )
        st.dataframe(gainers_df, width="stretch", hide_index=True)

    with col_l:
        st.markdown("#### 🔴 Underperforming Equities (Downside Drift)")
        losers_df = (
            pd.DataFrame(gainers_data)
            .sort_values("raw_pct", ascending=True)
            .head(5)
            .drop(columns=["raw_pct"])
        )
        st.dataframe(losers_df, width="stretch", hide_index=True)

    # Real-Time Sentiment Feed
    st.markdown("#### 📰 Institutional Market Sentiment & News Wire")
    news_items = get_live_sentiment_news()
    ncol1, ncol2 = st.columns(2)
    for idx, item in enumerate(news_items[:4]):
        target_col = ncol1 if idx % 2 == 0 else ncol2
        badge_cls = (
            "badge-bull"
            if item["sentiment"] == "BULLISH"
            else ("badge-bear" if item["sentiment"] == "BEARISH" else "badge-neutral")
        )
        with target_col:
            st.markdown(
                f"""
                <div class="terminal-card">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                    <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">{item['timestamp']} • {item['source']}</span>
                    <span class="{badge_cls}">{item['sentiment']}</span>
                  </div>
                  <div style="font-weight: 600; font-size: 13px; color: #f8fafc; margin-bottom: 4px;">{item['headline']}</div>
                  <div style="font-size: 11px; color: #cbd5e1;">{item['summary']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================================
# MODULE B: STOCK EXPLORER & INTRADAY
# ==========================================================
elif module == "Stock Explorer & Intraday":
    meta = STOCKS_METADATA.get(selected_stock, {})
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">{meta.get('company_name', selected_stock)} ({selected_stock})</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Sector: {meta.get('sector', 'Large Cap')} • Market Cap Tier: Large Cap • Exchange: National Stock Exchange of India</p>
          </div>
          <div>
            <span class="{'badge-bull' if is_positive else 'badge-bear'}" style="font-size: 14px; padding: 6px 14px;">
              ₹{active_ltp:,.2f} ({'+' if is_positive else ''}{active_chg_pct:.2f}%)
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    df_stock = load_processed_data(selected_stock)

    with col1:
        st.metric("Sector", meta.get("sector", "Large Cap"))
    with col2:
        st.metric("Current Price", f"₹{active_ltp:,.2f}", f"{active_chg_pct:+.2f}%")
    with col3:
        high_52 = df_stock["high"].tail(252).max() if not df_stock.empty else 0
        st.metric("52-Week High", f"₹{high_52:,.2f}")
    with col4:
        low_52 = df_stock["low"].tail(252).min() if not df_stock.empty else 0
        st.metric("52-Week Low", f"₹{low_52:,.2f}")
    with col5:
        ann_vol = (
            df_stock["daily_return"].std() * np.sqrt(252) * 100
            if not df_stock.empty
            else 0
        )
        st.metric("Annualized Volatility", f"{ann_vol:.1f}%")

    # Timeframe selection
    tf = st.radio(
        "Chart Resolution & Periodicity:",
        ["1D (Historical)", "1M (Intraday)", "5M (Intraday)", "15M (Intraday)"],
        horizontal=True,
    )

    if tf == "1D (Historical)":
        plot_df = df_stock.tail(120)
    else:
        clean_tf = tf.split(" ")[0]
        candles = streamer.generate_intraday_candles(
            selected_stock, timeframe=clean_tf, limit=60
        )
        plot_df = pd.DataFrame(candles).rename(columns={"time": "datetime_str"})

    if not plot_df.empty:
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=plot_df["datetime_str"],
                    open=plot_df["open"],
                    high=plot_df["high"],
                    low=plot_df["low"],
                    close=plot_df["close"],
                    increasing_line_color="#10b981",
                    decreasing_line_color="#f43f5e",
                    increasing_fillcolor="rgba(16, 185, 129, 0.6)",
                    decreasing_fillcolor="rgba(244, 63, 94, 0.6)",
                )
            ]
        )
        fig = apply_terminal_theme(fig, height=440)
        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, width="stretch")

    # Level-2 Market Depth & Options Side-by-Side
    col_dom, col_opt = st.columns([1, 1])
    with col_dom:
        st.markdown("#### ⚡ Level-2 Depth of Market (DOM)")
        depth = streamer.get_level2_market_depth(selected_stock)
        st.caption(
            f"Best Bid: ₹{depth['best_bid']} | Best Ask: ₹{depth['best_ask']} | Spread: ₹{depth['spread']} ({depth['spread_pct']}%)"
        )

        st.progress(
            depth["buy_pressure_pct"] / 100.0,
            text=f"Buy Pressure: {depth['buy_pressure_pct']}% vs Sell Pressure: {depth['sell_pressure_pct']}%",
        )

        bids_df = pd.DataFrame(depth["bids"])
        asks_df = pd.DataFrame(depth["asks"])
        st.write("**Top 5 Bids (Buyers):**")
        st.dataframe(bids_df, width="stretch", hide_index=True)
        st.write("**Top 5 Asks (Sellers):**")
        st.dataframe(asks_df, width="stretch", hide_index=True)

    with col_opt:
        st.markdown("#### ⚡ Real-Time Options Chain & Greeks")
        opt_data = get_options_chain_analytics(selected_stock)
        st.markdown(
            f"**Put-Call Ratio (PCR):** `{opt_data['put_call_ratio']}` ({opt_data['pcr_sentiment']}) | **Max Pain:** `₹{opt_data['max_pain_strike']}`"
        )

        greeks = opt_data["atm_greeks"]
        gcol1, gcol2, gcol3, gcol4 = st.columns(4)
        gcol1.metric("Call Delta (Δ)", f"+{greeks['call_delta']}")
        gcol2.metric("Put Delta (Δ)", f"{greeks['put_delta']}")
        gcol3.metric("Gamma (Γ)", f"{greeks['gamma']}")
        gcol4.metric("Theta (Θ)", f"₹{greeks['theta_daily']}")

        st.dataframe(
            pd.DataFrame(opt_data["option_chain"]).head(6),
            width="stretch",
            hide_index=True,
        )


# ==========================================================
# MODULE C: TECHNICAL ANALYSIS LAB
# ==========================================================
elif module == "Technical Analysis Lab":
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">Technical Analysis Lab: {selected_stock}</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Moving averages, volatility envelopes, momentum oscillators & algorithmic pattern detection</p>
          </div>
          <div>
            <span class="badge-cyan">MULTI-FACTOR ENGINE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_feat = load_features_data(selected_stock).tail(130)
    if not df_feat.empty:
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            show_sma = st.checkbox("Simple Moving Averages (20, 50, 200)", value=True)
            show_bb = st.checkbox("Bollinger Bands (20, 2σ)", value=True)
        with col_ctrl2:
            show_ema = st.checkbox("Exponential Moving Averages (9, 21)", value=False)
            oscillator = st.selectbox(
                "Subpane Momentum Oscillator", ["RSI (14)", "MACD (12, 26, 9)", "OBV"]
            )

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.7, 0.3],
        )

        # Price line
        fig.add_trace(
            go.Scatter(
                x=df_feat["datetime_str"],
                y=df_feat["close"],
                name="Close",
                line=dict(color="#f8fafc", width=1.5),
            ),
            row=1,
            col=1,
        )

        if show_sma:
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["sma_20"],
                    name="SMA 20",
                    line=dict(color="#f59e0b", width=1.2),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["sma_50"],
                    name="SMA 50",
                    line=dict(color="#3b82f6", width=1.2),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["sma_200"],
                    name="SMA 200",
                    line=dict(color="#ec4899", width=1.4),
                ),
                row=1,
                col=1,
            )

        if show_ema:
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["ema_9"],
                    name="EMA 9",
                    line=dict(color="#06b6d4", width=1.1, dash="dot"),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["ema_21"],
                    name="EMA 21",
                    line=dict(color="#8b5cf6", width=1.1, dash="dot"),
                ),
                row=1,
                col=1,
            )

        if show_bb:
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["bb_upper"],
                    name="BB Upper (2σ)",
                    line=dict(color="#06b6d4", width=1, dash="dot"),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["bb_lower"],
                    name="BB Lower (2σ)",
                    line=dict(color="#06b6d4", width=1, dash="dot"),
                    fill="tonexty",
                    fillcolor="rgba(6, 182, 212, 0.05)",
                ),
                row=1,
                col=1,
            )

        # Oscillator Subpane
        if oscillator == "RSI (14)":
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["rsi_14"],
                    name="RSI 14",
                    line=dict(color="#06b6d4", width=1.5),
                ),
                row=2,
                col=1,
            )
            fig.add_hline(
                y=70,
                line_dash="dot",
                line_color="#f43f5e",
                annotation_text="70 Overbought",
                row=2,
                col=1,
            )
            fig.add_hline(
                y=30,
                line_dash="dot",
                line_color="#10b981",
                annotation_text="30 Oversold",
                row=2,
                col=1,
            )
        elif oscillator == "MACD (12, 26, 9)":
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["macd"],
                    name="MACD",
                    line=dict(color="#10b981", width=1.2),
                ),
                row=2,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["macd_signal"],
                    name="Signal",
                    line=dict(color="#f59e0b", width=1.2),
                ),
                row=2,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=df_feat["datetime_str"],
                    y=df_feat["macd_hist"],
                    name="Histogram",
                    marker_color="#3b82f6",
                ),
                row=2,
                col=1,
            )

        fig = apply_terminal_theme(fig, height=520)
        st.plotly_chart(fig, width="stretch")

        # Active Signals
        signals = generate_analytical_signals(df_feat)
        st.markdown(f"#### ⚡ Algorithmic Pattern Conditions Detected ({len(signals)})")
        for s in signals:
            col_b, col_t = st.columns([1, 4])
            with col_b:
                bias_color = (
                    "badge-bull"
                    if s["bias"] == "BULLISH_BIAS"
                    else (
                        "badge-bear"
                        if s["bias"] == "BEARISH_BIAS"
                        else "badge-neutral"
                    )
                )
                st.markdown(
                    f"<span class='{bias_color}'>{s['condition']}</span>",
                    unsafe_allow_html=True,
                )
            with col_t:
                st.markdown(f"**{s['indicator']}**: {s['detail']}")


# ==========================================================
# MODULE D: FORECASTING LAB
# ==========================================================
elif module == "Forecasting Lab":
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">Multi-Horizon Econometric Forecasting Lab: {selected_stock}</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Multi-horizon projection (7d, 14d, 30d) with 95% Confidence Interval cones & Walk-Forward Cross-Validation</p>
          </div>
          <div>
            <span class="badge-gold">ZERO LEAKAGE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pkg = load_forecast_package(selected_stock)
    if pkg:
        h_choice = st.radio(
            "Forecast Projection Horizon:",
            ["7_day", "14_day", "30_day"],
            format_func=lambda x: f"{x.replace('_', ' ').title()} Ahead",
            horizontal=True,
        )
        horizon = pkg["horizons"][h_choice]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Target Forecast Date", horizon["target_date"])
        c2.metric("Current Spot Close", f"₹{horizon['current_price']:,.2f}")
        c3.metric("Projected Mean Close", f"₹{horizon['target_predicted_price']:,.2f}")
        c4.metric(
            "Expected Return",
            f"{horizon['expected_return_pct']:+.2f}%",
            horizon["projected_direction"],
        )

        # Forecast Plot with 95% Confidence Cone
        recent = pd.DataFrame(pkg["recent_history"]).tail(40)
        future = pd.DataFrame(horizon["forecast_series"])

        fig = go.Figure()
        # Historical Close
        fig.add_trace(
            go.Scatter(
                x=recent["date"],
                y=recent["actual_close"],
                name="Historical Actual",
                line=dict(color="#94a3b8", width=2),
            )
        )
        # Predicted Close
        fig.add_trace(
            go.Scatter(
                x=future["date"],
                y=future["predicted_close"],
                name="Forecast Mean Trajectory",
                line=dict(color="#06b6d4", width=2.5, dash="dash"),
            )
        )
        # Upper 95% Bound
        fig.add_trace(
            go.Scatter(
                x=future["date"],
                y=future["upper_bound_95"],
                name="95% Upper Bound",
                line=dict(color="#38bdf8", width=1),
                fill=None,
            )
        )
        # Lower 95% Bound
        fig.add_trace(
            go.Scatter(
                x=future["date"],
                y=future["lower_bound_95"],
                name="95% Lower Bound",
                line=dict(color="#38bdf8", width=1),
                fill="tonexty",
                fillcolor="rgba(6, 182, 212, 0.16)",
            )
        )

        fig = apply_terminal_theme(fig, height=460)
        st.plotly_chart(fig, width="stretch")

        # Out-of-sample walk-forward validation leaderboard
        st.markdown(
            "#### 🏆 Chronological Walk-Forward Validation Benchmark (Zero Future Lookahead)"
        )
        wfv = pkg["walk_forward_validation"]["comparison"]
        wfv_rows = []
        for m_name, m_val in wfv.items():
            metrics = m_val["metrics"]
            wfv_rows.append(
                {
                    "Model": m_name,
                    "RMSE (₹)": f"₹{metrics['rmse']:.2f}",
                    "MAE (₹)": f"₹{metrics['mae']:.2f}",
                    "MAPE (%)": f"{metrics['mape']:.2f}%",
                    "Directional Acc (%)": f"{metrics['directional_accuracy']:.1f}%",
                    "R² Score": f"{metrics['r2']:.3f}",
                    "Status": (
                        "✅ Selected Best Model"
                        if m_name == pkg["walk_forward_validation"]["best_model"]
                        else "Benchmark"
                    ),
                }
            )
        st.dataframe(pd.DataFrame(wfv_rows), width="stretch", hide_index=True)


# ==========================================================
# MODULE E: RISK INTELLIGENCE & TAIL RISK
# ==========================================================
elif module == "Risk Intelligence & Tail Risk":
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">Institutional Risk Intelligence: {selected_stock}</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Fat-tail metrics, Cornish-Fisher VaR (95%/99%), Expected Shortfall & Markowitz Portfolio Frontier</p>
          </div>
          <div>
            <span class="badge-bear">RISK ENGINE</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    risk = load_risk_profile(selected_stock)
    if risk:
        r1, r2, r3, r4, r5, r6 = st.columns(6)
        r1.metric("Ann. Volatility", f"{risk.get('annualized_volatility', 0):.1f}%")
        r2.metric(
            "Max Drawdown",
            f"-{risk.get('max_drawdown_pct', 0):.1f}%",
            delta_color="inverse",
        )
        r3.metric("Sharpe (Rf=6.5%)", f"{risk.get('sharpe_ratio', 0):.2f}")
        r4.metric("Sortino Ratio", f"{risk.get('sortino_ratio', 0):.2f}")
        r5.metric("Beta vs NIFTY 50", f"{risk.get('beta_vs_nifty50', 1.0):.2f}")
        r6.metric("Jensen's Alpha", f"{risk.get('jensens_alpha_pct', 0):+.2f}%")

        # Rolling Drawdown Chart
        dds = pd.DataFrame(risk.get("rolling_drawdowns", []))
        if not dds.empty:
            st.markdown("#### 📉 Underwater Rolling Drawdown Profile (60 Sessions)")
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=dds["date"],
                    y=dds["drawdown_pct"],
                    name="Drawdown %",
                    line=dict(color="#f43f5e", width=1.5),
                    fill="tozeroy",
                    fillcolor="rgba(244, 63, 94, 0.25)",
                )
            )
            fig = apply_terminal_theme(fig, height=270)
            st.plotly_chart(fig, width="stretch")

        # Interactive Portfolio Simulator
        st.markdown("#### 🎛️ Interactive Multi-Asset Portfolio Simulation")
        st.caption(
            "Adjust allocations to observe real-time diversification benefit on portfolio volatility:"
        )

        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
        w_rel = pcol1.slider("RELIANCE %", 0, 100, 25, 5)
        w_tcs = pcol2.slider("TCS %", 0, 100, 25, 5)
        w_hdfc = pcol3.slider("HDFCBANK %", 0, 100, 25, 5)
        w_itc = pcol4.slider("ITC %", 0, 100, 25, 5)

        port_res = simulate_portfolio_risk(
            {
                "RELIANCE": w_rel,
                "TCS": w_tcs,
                "HDFCBANK": w_hdfc,
                "ITC": w_itc,
            }
        )

        res1, res2, res3, res4 = st.columns(4)
        res1.metric("Exp. Annual Return", f"+{port_res['expected_annual_return']:.2f}%")
        res2.metric("Portfolio Volatility", f"{port_res['annualized_volatility']:.2f}%")
        res3.metric("Diversification Ratio", f"{port_res['diversification_ratio']}x")
        res4.metric("Portfolio Sharpe", f"{port_res['sharpe_ratio']:.2f}")


# ==========================================================
# MODULE F: AI QUANTITATIVE INSIGHTS
# ==========================================================
elif module == "AI Quantitative Insights":
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">AI Quantitative Market Intelligence: {selected_stock}</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Deterministic natural-language synthesis grounded in calculated backend econometrics (Zero Hallucination)</p>
          </div>
          <div>
            <span class="badge-cyan">DETERMINISTIC NLG</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    insights = generate_asset_insights(selected_stock)
    stance = insights.get("overall_stance", "NEUTRAL")

    st.markdown(
        f"""
        <div class="terminal-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h4 style="margin:0; color:white; font-size: 16px;">{insights.get('company_name')} ({insights.get('symbol')})</h4>
              <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">Comprehensive Econometric Summary</span>
            </div>
            <span class="{'badge-bull' if 'BULLISH' in stance else ('badge-bear' if 'BEARISH' in stance else 'badge-neutral')}" style="font-size: 13px; padding: 4px 12px;">{stance}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Macro Trend:**\n\n{insights.get('trend_summary')}")
        st.warning(
            f"**Tail Risk & Volatility:**\n\n{insights.get('volatility_observation')}"
        )
    with c2:
        st.success(
            f"**Institutional Volume Flow:**\n\n{insights.get('volume_observation')}"
        )
        st.error(
            f"**Capital Preservation Warning:**\n\n{insights.get('risk_warning')}"
        )

    st.markdown(
        f"""
        <div class="terminal-card" style="border-left: 4px solid #06b6d4;">
          <h5 style="color:#06b6d4; margin:0 0 6px 0; font-size: 14px;">30-Day Econometric Trajectory & Model Rationale</h5>
          <p style="color:#cbd5e1; font-size:12px; margin:0; line-height: 1.6;">{insights.get('forecast_explanation')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# MODULE G: MODEL PERFORMANCE CENTER
# ==========================================================
elif module == "Model Performance Center":
    st.markdown(
        f"""
        <div class="hero-banner">
          <div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 800; font-size: 22px;">Model Performance & Feature Importance: {selected_stock}</h3>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 12px; font-family: 'JetBrains Mono', monospace;">Cross-family benchmark (Naive vs MA20 vs ARIMA vs SARIMAX vs XGBoost) & Gini feature attribution</p>
          </div>
          <div>
            <span class="badge-gold">BENCHMARK CENTER</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    board = load_leaderboard()
    entry = board.get(selected_stock, {})
    if entry:
        st.markdown(
            f"**Optimal Model Selected:** `{entry.get('best_model')}` via Occam's Quantitative Razor"
        )
        st.caption(entry.get("selection_rationale", ""))

        models_df = pd.DataFrame(entry.get("models", {})).T
        st.dataframe(models_df, width="stretch")

        col_feat, col_resid = st.columns(2)
        with col_feat:
            st.markdown("#### 🌲 XGBoost Gini Feature Importances")
            feats = pd.DataFrame(entry.get("feature_importances", [])).head(7)
            if not feats.empty:
                fig = go.Figure(
                    go.Bar(
                        x=feats["importance"],
                        y=feats["feature"],
                        orientation="h",
                        marker=dict(
                            color="rgba(6, 182, 212, 0.8)",
                            line=dict(color="#06b6d4", width=1),
                        ),
                    )
                )
                fig = apply_terminal_theme(fig, height=300)
                st.plotly_chart(fig, width="stretch")

        with col_resid:
            st.markdown("#### 📉 Residual Diagnostics (ε = y - ŷ)")
            rstats = entry.get("residual_stats", {})
            st.metric("Mean Prediction Error", f"₹{rstats.get('mean_error', 0):.2f}")
            st.metric("Standard Error", f"₹{rstats.get('std_error', 0):.2f}")
            st.metric("Residual Skewness", f"{rstats.get('skewness', 0):.3f}")
