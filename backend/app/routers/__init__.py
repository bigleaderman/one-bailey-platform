"""
API 라우터 패키지
"""
from app.routers.predictions import router as predictions_router
from app.routers.market import router as market_router

__all__ = ["predictions_router", "market_router"]
