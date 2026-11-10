"""
MarketVision AI - Streamlit Institutional Terminal Edition
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
sys.path.append(BASE_DIR)

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

# Page Configuration
st.set_page_config(
    page_title="MarketVision AI - NSE Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Bloomberg-Inspired Dark Navy Financial Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #080c14;
        color: #f1f5f9;
    }
    
    .mono {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Terminal Cards */
    .terminal-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .stat-label {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-size: 20px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #ffffff;
    }
    
    .badge-bull {
        background: rgba(6, 78, 59, 0.7);
        color: #34d399;
        border: 1px solid #059669;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .badge-bear {
        background: rgba(127, 29, 29, 0.7);
        color: #f87171;
        border: 1px solid #dc2626;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 3px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    return pd.DataFrame()


@st.cache_data(ttl=300)
def load_features_data(symbol: str) -> pd.DataFrame:
    clean_sym = symbol.replace(" ", "_")
    p_path = os.path.join(FEATURES_DIR, f"{clean_sym}_features.parquet")
    if os.path.exists(p_path):
        return pd.read_parquet(p_path)
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


# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
      <div style="background: linear-gradient(135deg, #06b6d4, #3b82f6); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-family: monospace;">M</div>
      <div>
        <div style="font-weight: bold; font-family: monospace; font-size: 15px; color: white;">Market<span style="color: #06b6d4;">Vision</span> AI</div>
        <div style="font-size: 10px; color: #64748b; font-family: monospace;">STREAMLIT TERMINAL</div>
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

selected_stock = st.sidebar.selectbox("🎯 Select Active Asset", CORE_STOCKS, index=0)

module = st.sidebar.radio(
    "Terminal Modules",
    [
        "Market Overview",
        "Stock Explorer",
        "Technical Analysis Lab",
        "Forecasting Lab",
        "Risk Intelligence",
        "AI Market Insights",
        "Model Performance Center",
    ],
    index=0,
)

# Live Market Ticks
live_ticks = streamer.generate_live_ticks()
active_tick = live_ticks.get(selected_stock, {})
active_ltp = active_tick.get("ltp", 1000.0)
active_chg_pct = active_tick.get("pct_change", 0.0)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px;">
      <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase;">Active Quote ({selected_stock})</div>
      <div style="font-size: 18px; font-weight: bold; color: white; margin-top: 2px;">₹{active_ltp:,.2f}</div>
      <div style="color: {'#10b981' if active_chg_pct >= 0 else '#ef4444'}; font-weight: 600;">
        {'+' if active_chg_pct >= 0 else ''}{active_chg_pct:.2f}% ({active_tick.get('tick_direction', 'UP')})
      </div>
      <div style="color: #475569; font-size: 10px; margin-top: 4px;">{active_tick.get('timestamp', '')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption("🟢 Live Replay & Historical Certified Feeds")


# ---------------- TOP TICKER BAR ----------------
ticker_html = "<div style='display: flex; gap: 18px; background: #030712; padding: 8px 14px; border-radius: 8px; border: 1px solid #1e293b; overflow-x: auto; font-family: monospace; font-size: 12px; margin-bottom: 18px; white-space: nowrap;'>"
ticker_html += "<span style='color: #10b981; font-weight: bold;'>● LIVE STREAM</span>"
for sym in ["NIFTY_50", "NIFTY_BANK", "INDIA_VIX", "RELIANCE", "TCS", "HDFCBANK"]:
    t = live_ticks.get(sym, {})
    if t:
        pos = t["pct_change"] >= 0
        col = "#10b981" if pos else "#ef4444"
        ticker_html += f"<span><strong style='color:#94a3b8;'>{sym.replace('_',' ')}:</strong> <span style='color:white;'>₹{t['ltp']:,.2f}</span> <span style='color:{col}; font-weight:600;'>{'+' if pos else ''}{t['pct_change']:.2f}%</span></span>"
ticker_html += "</div>"
st.markdown(ticker_html, unsafe_allow_html=True)


# ==========================================================
# MODULE A: MARKET OVERVIEW
# ==========================================================
if module == "Market Overview":
    st.markdown("### 📊 National Stock Exchange (NSE) Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nifty = live_ticks.get("NIFTY_50", {})
        st.metric(
            "NIFTY 50",
            f"₹{nifty.get('ltp', 24994.70):,.2f}",
            f"{nifty.get('pct_change', 0.42):+.2f}%",
        )
    with col2:
        bank = live_ticks.get("NIFTY_BANK", {})
        st.metric(
            "NIFTY BANK",
            f"₹{bank.get('ltp', 52810.15):,.2f}",
            f"{bank.get('pct_change', 0.38):+.2f}%",
        )
    with col3:
        it = live_ticks.get("NIFTY_IT", {})
        st.metric(
            "NIFTY IT",
            f"₹{it.get('ltp', 42190.80):,.2f}",
            f"{it.get('pct_change', -0.24):+.2f}%",
        )
    with col4:
        vix = live_ticks.get("INDIA_VIX", {})
        st.metric(
            "INDIA VIX (Volatility)",
            f"{vix.get('ltp', 14.85):.2f}",
            f"{vix.get('pct_change', -2.10):+.2f}%",
            delta_color="inverse",
        )

    # NIFTY 50 Candlestick Chart
    nifty_df = load_processed_data("NIFTY_50").tail(90)
    if not nifty_df.empty:
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
                decreasing_line_color="#ef4444",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                x=nifty_df["datetime_str"],
                y=nifty_df["volume"],
                name="Volume",
                marker_color="rgba(56, 189, 248, 0.4)",
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#090d16",
            height=460,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_rangeslider_visible=False,
            font=dict(family="JetBrains Mono", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gainers & Losers Tables
    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("#### 🟢 Top Performing Equities")
        gainers_data = []
        for s in CORE_STOCKS:
            t = live_ticks.get(s, {})
            gainers_data.append(
                {
                    "Symbol": s,
                    "LTP": f"₹{t.get('ltp', 0):,.2f}",
                    "Change %": f"{t.get('pct_change', 0):+.2f}%",
                    "raw_pct": t.get("pct_change", 0),
                }
            )
        gainers_df = (
            pd.DataFrame(gainers_data)
            .sort_values("raw_pct", ascending=False)
            .head(4)
            .drop(columns=["raw_pct"])
        )
        st.dataframe(gainers_df, use_container_width=True, hide_index=True)

    with col_l:
        st.markdown("#### 🔴 Underperforming Equities")
        losers_df = (
            pd.DataFrame(gainers_data)
            .sort_values("raw_pct", ascending=True)
            .head(4)
            .drop(columns=["raw_pct"])
        )
        st.dataframe(losers_df, use_container_width=True, hide_index=True)


# ==========================================================
# MODULE B: STOCK EXPLORER
# ==========================================================
elif module == "Stock Explorer":
    st.markdown(f"### 🔍 Stock Explorer: {selected_stock}")
    meta = STOCKS_METADATA.get(selected_stock, {})

    col1, col2, col3, col4, col5 = st.columns(5)
    df_stock = load_processed_data(selected_stock)

    with col1:
        st.metric("Sector", meta.get("sector", "Large Cap"))
    with col2:
        st.metric(
            "Current Price",
            f"₹{active_ltp:,.2f}",
            f"{active_chg_pct:+.2f}%",
        )
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
        "Resolution:",
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
                    decreasing_line_color="#ef4444",
                )
            ]
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#090d16",
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False,
            font=dict(family="JetBrains Mono", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Level-2 Market Depth & Options Side-by-Side
    col_dom, col_opt = st.columns([1, 1])
    with col_dom:
        st.markdown("#### ⚡ Level-2 Depth of Market (DOM)")
        depth = streamer.get_level2_market_depth(selected_stock)
        st.caption(
            f"Best Bid: ₹{depth['best_bid']} | Best Ask: ₹{depth['best_ask']} | Spread: ₹{depth['spread']}"
        )

        st.progress(
            depth["buy_pressure_pct"] / 100.0,
            text=f"Buy Pressure: {depth['buy_pressure_pct']}% vs Sell: {depth['sell_pressure_pct']}%",
        )

        bids_df = pd.DataFrame(depth["bids"])
        asks_df = pd.DataFrame(depth["asks"])
        st.write("**Top 5 Bids (Buyers):**")
        st.dataframe(bids_df, use_container_width=True, hide_index=True)
        st.write("**Top 5 Asks (Sellers):**")
        st.dataframe(asks_df, use_container_width=True, hide_index=True)

    with col_opt:
        st.markdown("#### ⚡ Options & Greeks Snapshot")
        opt_data = get_options_chain_analytics(selected_stock)
        st.markdown(
            f"**Put-Call Ratio (PCR):** `{opt_data['put_call_ratio']}` ({opt_data['pcr_sentiment']})"
        )
        st.markdown(f"**Max Pain Strike:** `₹{opt_data['max_pain_strike']}`")

        greeks = opt_data["atm_greeks"]
        gcol1, gcol2, gcol3, gcol4 = st.columns(4)
        gcol1.metric("Call Delta (Δ)", f"+{greeks['call_delta']}")
        gcol2.metric("Put Delta (Δ)", f"{greeks['put_delta']}")
        gcol3.metric("Gamma (Γ)", f"{greeks['gamma']}")
        gcol4.metric("Theta (Θ)", f"₹{greeks['theta_daily']}")

        st.dataframe(
            pd.DataFrame(opt_data["option_chain"]).head(6),
            use_container_width=True,
            hide_index=True,
        )


# ==========================================================
# MODULE C: TECHNICAL ANALYSIS LAB
# ==========================================================
elif module == "Technical Analysis Lab":
    st.markdown(f"### 📈 Technical Analysis Lab: {selected_stock}")

    df_feat = load_features_data(selected_stock).tail(120)
    if not df_feat.empty:
        # Overlays
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            show_sma = st.checkbox("Simple Moving Averages (20, 50, 200)", value=True)
            show_bb = st.checkbox("Bollinger Bands (20, 2σ)", value=True)
        with col_ctrl2:
            show_ema = st.checkbox("Exponential Moving Averages (9, 21)", value=False)
            oscillator = st.selectbox(
                "Subpane Oscillator", ["RSI (14)", "MACD (12, 26, 9)", "OBV"]
            )

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.7, 0.3],
        )

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
                    line=dict(color="#f59e0b", width=1),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["sma_50"],
                    name="SMA 50",
                    line=dict(color="#3b82f6", width=1),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["sma_200"],
                    name="SMA 200",
                    line=dict(color="#ec4899", width=1.2),
                ),
                row=1,
                col=1,
            )

        if show_bb:
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["bb_upper"],
                    name="BB Upper",
                    line=dict(color="#06b6d4", width=1, dash="dot"),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_feat["datetime_str"],
                    y=df_feat["bb_lower"],
                    name="BB Lower",
                    line=dict(color="#06b6d4", width=1, dash="dot"),
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
                line_color="#ef4444",
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

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#090d16",
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family="JetBrains Mono", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Active Signals
        signals = generate_analytical_signals(df_feat)
        st.markdown(f"#### ⚡ Active Analytical Condition Flags ({len(signals)})")
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
    st.markdown(f"### 🔮 Econometric & ML Forecasting Lab: {selected_stock}")

    pkg = load_forecast_package(selected_stock)
    if pkg:
        h_choice = st.radio(
            "Select Forecast Horizon:",
            ["7_day", "14_day", "30_day"],
            format_func=lambda x: f"{x.replace('_', ' ').title()} Ahead",
            horizontal=True,
        )
        horizon = pkg["horizons"][h_choice]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Target Date", horizon["target_date"])
        c2.metric("Current Price", f"₹{horizon['current_price']:,.2f}")
        c3.metric("Projected Close", f"₹{horizon['target_predicted_price']:,.2f}")
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
                name="Forecast Projection",
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
                fillcolor="rgba(6, 182, 212, 0.15)",
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#090d16",
            height=440,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family="JetBrains Mono", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Out-of-sample walk-forward validation leaderboard
        st.markdown("#### 🏆 Chronological Walk-Forward Validation Benchmark")
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
                        "✅ Best Model"
                        if m_name == pkg["walk_forward_validation"]["best_model"]
                        else "Benchmark"
                    ),
                }
            )
        st.dataframe(pd.DataFrame(wfv_rows), use_container_width=True, hide_index=True)


# ==========================================================
# MODULE E: RISK INTELLIGENCE
# ==========================================================
elif module == "Risk Intelligence":
    st.markdown(f"### 🛡️ Risk Intelligence & Tail Risk: {selected_stock}")

    risk = load_risk_profile(selected_stock)
    if risk:
        r1, r2, r3, r4, r5, r6 = st.columns(6)
        r1.metric("Ann. Volatility", f"{risk.get('annualized_volatility', 0):.1f}%")
        r2.metric(
            "Max Drawdown",
            f"-{risk.get('max_drawdown_pct', 0):.1f}%",
            delta_color="inverse",
        )
        r3.metric("Sharpe Ratio", f"{risk.get('sharpe_ratio', 0):.2f}")
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
                    line=dict(color="#ef4444", width=1.5),
                    fill="tozeroy",
                    fillcolor="rgba(239, 68, 68, 0.25)",
                )
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                plot_bgcolor="#090d16",
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(family="JetBrains Mono", size=11),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Interactive Portfolio Simulator
        st.markdown("#### 🎛️ Interactive Multi-Asset Portfolio Simulation")
        st.caption("Adjust allocations to observe diversification benefit:")

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
# MODULE F: AI MARKET INSIGHTS
# ==========================================================
elif module == "AI Market Insights":
    st.markdown(f"### 🤖 AI Quantitative Market Intelligence: {selected_stock}")

    insights = generate_asset_insights(selected_stock)
    stance = insights.get("overall_stance", "NEUTRAL")

    st.markdown(
        f"""
        <div class="terminal-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <h4 style="margin:0; color:white;">{insights.get('company_name')} ({insights.get('symbol')})</h4>
            <span class="{'badge-bull' if 'BULLISH' in stance else ('badge-bear' if 'BEARISH' in stance else 'badge-neutral')}">{stance}</span>
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
          <h5 style="color:#06b6d4; margin:0 0 6px 0;">30-Day Econometric Trajectory & Model Rationale</h5>
          <p style="color:#cbd5e1; font-size:12px; margin:0;">{insights.get('forecast_explanation')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# MODULE G: MODEL PERFORMANCE CENTER
# ==========================================================
elif module == "Model Performance Center":
    st.markdown(f"### 🏆 Model Performance Center: {selected_stock}")

    board = load_leaderboard()
    entry = board.get(selected_stock, {})
    if entry:
        st.markdown(
            f"**Optimal Model Selected:** `{entry.get('best_model')}` via Occam's Quantitative Razor"
        )
        st.caption(entry.get("selection_rationale", ""))

        models_df = pd.DataFrame(entry.get("models", {})).T
        st.dataframe(models_df, use_container_width=True)

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
                        marker_color="#06b6d4",
                    )
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#090d16",
                    height=280,
                    margin=dict(l=10, r=10, t=10, b=10),
                    font=dict(family="JetBrains Mono", size=10),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_resid:
            st.markdown("#### 📉 Residual Diagnostics (ε = y - ŷ)")
            rstats = entry.get("residual_stats", {})
            st.metric("Mean Prediction Error", f"₹{rstats.get('mean_error', 0):.2f}")
            st.metric("Standard Error", f"₹{rstats.get('std_error', 0):.2f}")
            st.metric("Residual Skewness", f"{rstats.get('skewness', 0):.3f}")
