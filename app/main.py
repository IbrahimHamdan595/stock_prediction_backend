from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import (
    analytics as analytics_router,
    auth as auth_router,
    backtests as backtests_router,
    market_data as market_data_router,
    news as news_router,
    signals as signals_router,
    strategies as strategies_router,
    users as users_router,
)
from app.core.config import settings
from app.db.mongo import lifespan


def create_app() -> FastAPI:
    app = FastAPI(title="Stock Prediction & Trading Signals API", version="1.0.0", lifespan=lifespan)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users_router.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(market_data_router.router, prefix="/api/v1/market-data", tags=["market-data"])
    app.include_router(news_router.router, prefix="/api/v1/news", tags=["news"])
    app.include_router(strategies_router.router, prefix="/api/v1/strategies", tags=["strategies"])
    app.include_router(signals_router.router, prefix="/api/v1/signals", tags=["signals"])
    app.include_router(backtests_router.router, prefix="/api/v1/backtests", tags=["backtests"])
    app.include_router(analytics_router.router, prefix="/api/v1", tags=["analytics"])
    return app


app = create_app()
