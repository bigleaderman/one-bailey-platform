"""
시장 관련 API 엔드포인트
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.market import MonthlyTrendResponse, MarketIndicatorsResponse, DateMarketResponse, MarketTrendResponse, MarketSummaryResponse, MarketIndicatorDetailResponse, EconomicDetailResponse, NewsResponse, NewsItem
from sqlalchemy import text as sql_text
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


@router.get("/trend", response_model=MarketTrendResponse)
def get_market_trend(days: int = 30, db: Session = Depends(get_db)):
    """최근 N일 시계열 데이터 (차트용)"""
    return MarketService.get_market_trend(db, min(days, 90))


@router.get("/summary", response_model=MarketSummaryResponse)
def get_market_summary(db: Session = Depends(get_db)):
    """시장 종합 상태 (온도계 + 지표 카드 + 경제 지표)"""
    try:
        return MarketService.get_market_summary(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/indicator/{indicator_name}", response_model=MarketIndicatorDetailResponse)
def get_market_indicator_detail(indicator_name: str, db: Session = Depends(get_db)):
    """시장 지표 상세 (해설 + 시계열)"""
    result = MarketService.get_market_indicator_detail(db, indicator_name)
    if not result:
        raise HTTPException(status_code=404, detail="해당 시장 지표를 찾을 수 없습니다")
    return result


@router.get("/economic/{indicator_name}", response_model=EconomicDetailResponse)
def get_economic_detail(indicator_name: str, db: Session = Depends(get_db)):
    """경제 지표 상세 정보 (해설 + 시계열)"""
    result = MarketService.get_economic_detail(db, indicator_name)
    if not result:
        raise HTTPException(status_code=404, detail="해당 경제 지표를 찾을 수 없습니다")
    return result


@router.get("/news", response_model=NewsResponse)
def get_latest_news(db: Session = Depends(get_db)):
    """최신 시장 뉴스 헤드라인"""
    rows = db.execute(sql_text("""
        SELECT headline, source, news_datetime, symbol, data_date, headline_ko, summary_ko
        FROM market_news
        ORDER BY data_date DESC, news_datetime DESC NULLS LAST
        LIMIT 10
    """)).fetchall()

    if not rows:
        return NewsResponse(date="", items=[])

    data_date = str(rows[0][4]) if rows[0][4] else ""
    items = [
        NewsItem(
            headline=r[0],
            source=r[1] or "",
            datetime=r[2].strftime("%H:%M") if r[2] else None,
            symbol=r[3] or "",
            headline_ko=r[5],
            summary_ko=r[6],
        )
        for r in rows
    ]

    return NewsResponse(date=data_date, items=items)


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
