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


class DateMarketResponse(BaseModel):
    """날짜별 시장 지표 응답 (상세 페이지용)"""
    qqq_price: Optional[float] = None
    vix_level: Optional[float] = None
    nq_future: Optional[float] = None
    nq_change: Optional[float] = None
    dxy_level: Optional[float] = None
    dxy_change: Optional[float] = None
    treasury_10y: Optional[float] = None
    gold_price: Optional[float] = None
    data_date: Optional[str] = None
