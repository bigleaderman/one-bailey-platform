"""
시장 관련 스키마
"""
from pydantic import BaseModel
from typing import Optional, List


class WeeklyTrend(BaseModel):
    """주간 트렌드"""
    week_number: int
    week_label: str
    start_date: str
    end_date: str
    direction: str
    direction_text: str
    total_change: float
    summary: str
    is_current_week: bool


class MonthlyTrendResponse(BaseModel):
    """월간 시장 흐름 응답"""
    month: str
    weeks: List[WeeklyTrend]


class MarketIndicator(BaseModel):
    """개별 시장 지표"""
    name: str
    label: str
    value: Optional[float]
    unit: str
    status: str
    status_text: str


class MarketIndicatorsResponse(BaseModel):
    """시장 지표 응답"""
    date: str
    indicators: List[MarketIndicator]
