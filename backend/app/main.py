"""
OneBailey Backend - FastAPI Application
DB에서 predictions 데이터를 조회하여 프론트엔드에 제공
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, Numeric, Date, DateTime, Text, JSON, desc, cast, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, timedelta
import os

# ============================================
# Database Configuration
# ============================================
DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "onebailey")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# Models
# ============================================
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(Date, nullable=False)
    direction = Column(String(10), nullable=False)
    confidence = Column(Float, nullable=False)
    actual_direction = Column(String(10), nullable=True)
    actual_change = Column(Float, nullable=True)
    key_factors = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    llm_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    qqq_price = Column(Numeric(10, 2), nullable=True)
    qqq_volume = Column(BigInteger, nullable=True)
    vix_level = Column(Numeric(5, 2), nullable=True)
    nq_future = Column(Numeric(10, 2), nullable=True)
    nq_change = Column(Numeric(5, 2), nullable=True)
    sox_index = Column(Numeric(10, 2), nullable=True)
    sox_change = Column(Numeric(5, 2), nullable=True)
    dxy_level = Column(Numeric(6, 2), nullable=True)
    dxy_change = Column(Numeric(5, 2), nullable=True)
    treasury_10y = Column(Numeric(5, 3), nullable=True)
    treasury_2y = Column(Numeric(5, 3), nullable=True)
    spread_2_10y = Column(Numeric(5, 3), nullable=True)
    fed_funds_rate = Column(Numeric(5, 3), nullable=True)
    tga_balance = Column(Numeric(12, 2), nullable=True)
    fed_balance_sheet = Column(Numeric(14, 2), nullable=True)
    m2_money_supply = Column(Numeric(14, 2), nullable=True)
    m2_yoy_change = Column(Numeric(5, 2), nullable=True)
    wti_oil = Column(Numeric(6, 2), nullable=True)
    gold_price = Column(Numeric(7, 2), nullable=True)
    collection_meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# ============================================
# Schemas
# ============================================
class TodayPredictionResponse(BaseModel):
    date: str
    date_iso: str
    direction: str
    direction_text: str
    confidence: float
    confidence_percent: int
    confidence_stars: int
    summary: str
    key_factors: List[str]
    risk_factors: List[str]


class PredictionDetailResponse(BaseModel):
    date: str
    date_iso: str
    direction: str
    direction_text: str
    confidence: float
    confidence_percent: int
    confidence_stars: int
    summary: str
    key_factors: List[str]
    risk_factors: List[str]
    actual_direction: Optional[str] = None
    actual_change: Optional[float] = None
    is_correct: Optional[bool] = None


class MarketIndicatorsResponse(BaseModel):
    qqq_price: Optional[float] = None
    vix_level: Optional[float] = None
    nq_future: Optional[float] = None
    nq_change: Optional[float] = None
    sox_index: Optional[float] = None
    sox_change: Optional[float] = None
    dxy_level: Optional[float] = None
    dxy_change: Optional[float] = None
    treasury_10y: Optional[float] = None
    treasury_2y: Optional[float] = None
    spread_2_10y: Optional[float] = None
    wti_oil: Optional[float] = None
    gold_price: Optional[float] = None
    data_date: Optional[str] = None


class RecentPredictionItem(BaseModel):
    date: str
    date_iso: str
    direction: str
    actual_direction: Optional[str] = None
    actual_change: Optional[float] = None
    is_correct: Optional[bool] = None


class StatsResponse(BaseModel):
    period: str
    total: int
    correct: int
    accuracy: float


class PredictionResponse(BaseModel):
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

# ============================================
# Helpers
# ============================================
DIRECTION_MAP = {
    "UP": "상승 예상",
    "DOWN": "하락 예상",
    "HOLD": "보합 예상"
}


def calc_confidence(confidence_raw):
    percent = int(confidence_raw * 100) if confidence_raw <= 1 else int(confidence_raw)
    stars = min(5, max(1, int(percent / 20)))
    return percent, stars


def parse_factors(raw):
    if isinstance(raw, list):
        return raw[:5]
    return []

# ============================================
# FastAPI App
# ============================================
app = FastAPI(
    title="OneBailey API",
    description="QQQ ETF 예측 서비스 API",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# Routes
# ============================================
@app.get("/")
async def root():
    return {"status": "ok", "message": "OneBailey API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/predictions/today", response_model=TodayPredictionResponse)
def get_today_prediction(db: Session = Depends(get_db)):
    """오늘의 예측 조회 (가장 최근 데이터)"""
    today = date.today()

    prediction = db.query(Prediction)\
        .filter(Prediction.prediction_date <= today)\
        .order_by(desc(Prediction.prediction_date))\
        .first()

    if not prediction:
        raise HTTPException(status_code=404, detail="예측 데이터가 없습니다")

    confidence_percent, confidence_stars = calc_confidence(prediction.confidence)

    return TodayPredictionResponse(
        date=prediction.prediction_date.strftime("%Y년 %m월 %d일"),
        date_iso=prediction.prediction_date.isoformat(),
        direction=prediction.direction,
        direction_text=DIRECTION_MAP.get(prediction.direction, prediction.direction),
        confidence=prediction.confidence,
        confidence_percent=confidence_percent,
        confidence_stars=confidence_stars,
        summary=prediction.summary or "예측 요약이 없습니다.",
        key_factors=parse_factors(prediction.key_factors),
        risk_factors=parse_factors(prediction.risk_factors),
    )


@app.get("/api/predictions/recent", response_model=List[RecentPredictionItem])
def get_recent_predictions(days: int = 7, db: Session = Depends(get_db)):
    """최근 N일 예측 기록 (상세페이지 하단용)"""
    predictions = db.query(Prediction)\
        .filter(Prediction.actual_direction.isnot(None))\
        .order_by(desc(Prediction.prediction_date))\
        .limit(days)\
        .all()

    result = []
    for p in predictions:
        is_correct = None
        if p.actual_direction:
            is_correct = p.direction == p.actual_direction
        result.append(RecentPredictionItem(
            date=p.prediction_date.strftime("%m/%d"),
            date_iso=p.prediction_date.isoformat(),
            direction=p.direction,
            actual_direction=p.actual_direction,
            actual_change=float(p.actual_change) if p.actual_change is not None else None,
            is_correct=is_correct,
        ))

    return result


@app.get("/api/predictions/stats", response_model=List[StatsResponse])
def get_prediction_stats(db: Session = Depends(get_db)):
    """적중률 통계 (7일, 30일, 전체)"""
    today = date.today()
    result = []

    for label, days in [("7d", 7), ("30d", 30), ("all", None)]:
        query = db.query(Prediction).filter(Prediction.actual_direction.isnot(None))
        if days:
            since = today - timedelta(days=days)
            query = query.filter(Prediction.prediction_date >= since)

        preds = query.all()
        total = len(preds)
        correct = sum(1 for p in preds if p.direction == p.actual_direction)
        accuracy = round(correct / total * 100, 1) if total > 0 else 0.0

        result.append(StatsResponse(
            period=label,
            total=total,
            correct=correct,
            accuracy=accuracy,
        ))

    return result


@app.get("/api/predictions/date/{pred_date}", response_model=PredictionDetailResponse)
def get_prediction_by_date(pred_date: str, db: Session = Depends(get_db)):
    """날짜 기반 예측 상세 조회"""
    try:
        target = datetime.strptime(pred_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식: YYYY-MM-DD")

    prediction = db.query(Prediction)\
        .filter(Prediction.prediction_date == target)\
        .first()

    if not prediction:
        raise HTTPException(status_code=404, detail="해당 날짜의 예측이 없습니다")

    confidence_percent, confidence_stars = calc_confidence(prediction.confidence)

    is_correct = None
    if prediction.actual_direction:
        is_correct = prediction.direction == prediction.actual_direction

    return PredictionDetailResponse(
        date=prediction.prediction_date.strftime("%Y년 %m월 %d일"),
        date_iso=prediction.prediction_date.isoformat(),
        direction=prediction.direction,
        direction_text=DIRECTION_MAP.get(prediction.direction, prediction.direction),
        confidence=prediction.confidence,
        confidence_percent=confidence_percent,
        confidence_stars=confidence_stars,
        summary=prediction.summary or "예측 요약이 없습니다.",
        key_factors=parse_factors(prediction.key_factors),
        risk_factors=parse_factors(prediction.risk_factors),
        actual_direction=prediction.actual_direction,
        actual_change=float(prediction.actual_change) if prediction.actual_change is not None else None,
        is_correct=is_correct,
    )


@app.get("/api/predictions/date/{pred_date}/market", response_model=MarketIndicatorsResponse)
def get_market_for_date(pred_date: str, db: Session = Depends(get_db)):
    """해당 날짜 시장 지표 조회"""
    try:
        target = datetime.strptime(pred_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식: YYYY-MM-DD")

    # data_date가 target의 직전 거래일 또는 target 자체에 해당하는 데이터를 조회
    row = db.query(MarketData)\
        .filter(
            MarketData.collection_meta['data_date'].astext <= pred_date,
            MarketData.collection_meta['collection_type'].astext != 'closing_price',
            MarketData.qqq_price.isnot(None),
        )\
        .order_by(desc(MarketData.collection_meta['data_date'].astext))\
        .first()

    if not row:
        raise HTTPException(status_code=404, detail="해당 날짜의 시장 데이터가 없습니다")

    meta = row.collection_meta or {}

    return MarketIndicatorsResponse(
        qqq_price=float(row.qqq_price) if row.qqq_price else None,
        vix_level=float(row.vix_level) if row.vix_level else None,
        nq_future=float(row.nq_future) if row.nq_future else None,
        nq_change=float(row.nq_change) if row.nq_change else None,
        sox_index=float(row.sox_index) if row.sox_index else None,
        sox_change=float(row.sox_change) if row.sox_change else None,
        dxy_level=float(row.dxy_level) if row.dxy_level else None,
        dxy_change=float(row.dxy_change) if row.dxy_change else None,
        treasury_10y=float(row.treasury_10y) if row.treasury_10y else None,
        treasury_2y=float(row.treasury_2y) if row.treasury_2y else None,
        spread_2_10y=float(row.spread_2_10y) if row.spread_2_10y else None,
        wti_oil=float(row.wti_oil) if row.wti_oil else None,
        gold_price=float(row.gold_price) if row.gold_price else None,
        data_date=meta.get('data_date'),
    )


@app.get("/api/predictions", response_model=List[PredictionResponse])
def get_predictions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """예측 목록 조회"""
    predictions = db.query(Prediction)\
        .order_by(desc(Prediction.prediction_date))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return predictions


@app.get("/api/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """특정 예측 조회"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="예측을 찾을 수 없습니다")
    return prediction
