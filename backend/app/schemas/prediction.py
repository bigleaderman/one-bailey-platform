"""
예측 관련 스키마
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class TodayPredictionResponse(BaseModel):
    """오늘의 예측 응답"""
    date: str
    direction: str
    direction_text: str
    confidence: float
    confidence_percent: int
    confidence_stars: int
    summary: str
    key_factors: List[str]
    risk_factors: List[str]


class PredictionResponse(BaseModel):
    """예측 상세 응답"""
    id: int
    prediction_date: date
    direction: str
    confidence: float
    summary: Optional[str] = None
    key_factors: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionHistoryItem(BaseModel):
    """개별 예측 기록"""
    date: str
    date_short: str
    direction: str
    direction_text: str
    actual_direction: Optional[str]
    actual_change: Optional[float]
    is_correct: Optional[bool]


class PredictionHistoryResponse(BaseModel):
    """예측 기록 응답"""
    history: List[PredictionHistoryItem]
    stats: dict
