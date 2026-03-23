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


# ============================================
# 시장 현황 페이지용 스키마
# ============================================
class TrendDataPoint(BaseModel):
    """차트용 시계열 데이터 포인트"""
    date: str
    qqq_price: Optional[float] = None
    vix_level: Optional[float] = None
    treasury_10y: Optional[float] = None
    dxy_level: Optional[float] = None
    gold_price: Optional[float] = None
    wti_oil: Optional[float] = None


class MarketTrendResponse(BaseModel):
    """시장 추세 차트 데이터"""
    data: List[TrendDataPoint]
    days: int


class IndicatorCard(BaseModel):
    """지표 카드 (상태 + 해설)"""
    name: str
    label: str
    value: Optional[float] = None
    change: Optional[float] = None
    unit: str
    trend: str          # up, down, stable
    trend_text: str     # ↗ 상승중, ↘ 하락중, → 안정
    status: str         # good, neutral, bad
    description: str    # 쉬운 해설


class MarketTemperature(BaseModel):
    """시장 온도계"""
    score: int          # 0~100 (0=극도 공포, 100=극도 탐욕)
    label: str          # 공포, 불안, 중립, 낙관, 탐욕
    emoji: str
    description: str    # 한 줄 해설


class EconomicIndicatorCard(BaseModel):
    """경제 지표 카드"""
    category: str       # 물가, 고용, 성장
    name: str
    label: str
    value: Optional[float] = None
    change: Optional[float] = None
    unit: str
    description: str


class MarketSummaryResponse(BaseModel):
    """시장 현황 종합 응답"""
    temperature: MarketTemperature
    indicators: List[IndicatorCard]
    economic: List[EconomicIndicatorCard]
    updated_at: str
