"""
MarketVision AI - FastAPI Main Application Server
Institutional Stock Market Forecasting & Risk Intelligence Platform (NSE)
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure backend modules can be resolved
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.routes import router
from backend.api.realtime_routes import router as realtime_router, options_router, sentiment_router

app = FastAPI(
    title="MarketVision AI - Institutional Financial Intelligence API",
    description=(
        "Production-grade financial analytics and machine learning forecasting platform "
        "tailored for the Indian National Stock Exchange (NSE). Combines econometric models, "
        "XGBoost machine learning, technical analysis indicators, portfolio risk intelligence, "
        "and AI-synthesized insights."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for development and deployment (Vercel & Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5180",
        "http://127.0.0.1:5180",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Production allows deployment frontend domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(router)
app.include_router(realtime_router)
app.include_router(options_router)
app.include_router(sentiment_router)


@app.get("/", tags=["Root"])
def root_entrypoint():
    """Root endpoint welcoming visitors and directing to interactive documentation."""
    return {
        "platform": "MarketVision AI",
        "tagline": "Stock Market Forecasting & Risk Intelligence Platform (NSE)",
        "docs_url": "/docs",
        "health_check": "/api/health",
        "version": "1.0.0",
        "author": "Quantitative Data Science & Financial Engineering Team"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
