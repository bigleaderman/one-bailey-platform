"""
시장 관련 API 엔드포인트
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.market import MonthlyTrendResponse, MarketIndicatorsResponse, DateMarketResponse
from app.services.market_service import MarketService


router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/monthly-trend", response_model=MonthlyTrendResponse)
def get_monthly_trend(db: Session = Depends(get_db)):
    """
    최근 4주 시장 흐름
    - 이번주 포함 최근 4주 데이터
    - 복리 방식 주간 변동률
    """
    return MarketService.get_monthly_trend(db)


@router.get("/indicators", response_model=MarketIndicatorsResponse)
def get_market_indicators(db: Session = Depends(get_db)):
    """
    주요 시장 지표
    - VIX, 나스닥 선물, 금리 등 6개 지표
    """
    return MarketService.get_market_indicators(db)


@router.get("/date/{target_date}", response_model=DateMarketResponse)
def get_market_for_date(target_date: str, db: Session = Depends(get_db)):
    """특정 날짜의 시장 지표 (상세 페이지용)"""
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식: YYYY-MM-DD")

    result = MarketService.get_market_for_date(db, target_date)
    if not result:
        raise HTTPException(status_code=404, detail="해당 날짜의 시장 데이터가 없습니다")
    return result
