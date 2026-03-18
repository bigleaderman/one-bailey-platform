"""
Pydantic 스키마 패키지
- API 요청/응답 모델 정의
"""
from app.schemas.prediction import (
    TodayPredictionResponse,
    PredictionResponse,
    PredictionDetailResponse,
    PredictionHistoryItem,
    PredictionHistoryResponse
)
from app.schemas.market import (
    WeeklyTrend,
    MonthlyTrendResponse,
    MarketIndicator,
    MarketIndicatorsResponse
)

__all__ = [
    "TodayPredictionResponse",
    "PredictionResponse",
    "PredictionDetailResponse",
    "PredictionHistoryItem",
    "PredictionHistoryResponse",
    "WeeklyTrend",
    "MonthlyTrendResponse",
    "MarketIndicator",
    "MarketIndicatorsResponse"
]
