"""
OneBailey Backend - FastAPI Application
DB에서 predictions 데이터를 조회하여 프론트엔드에 제공
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, JSON, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
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
    direction = Column(String(10), nullable=False)  # UP, DOWN, HOLD
    confidence = Column(Float, nullable=False)
    actual_direction = Column(String(10), nullable=True)
    actual_change = Column(Float, nullable=True)
    key_factors = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    llm_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# ============================================
# Schemas
# ============================================
class TodayPredictionResponse(BaseModel):
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
# FastAPI App
# ============================================
app = FastAPI(
    title="OneBailey API",
    description="QQQ ETF 예측 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
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
    
    # 오늘 또는 가장 최근 예측 조회
    prediction = db.query(Prediction)\
        .filter(Prediction.prediction_date <= today)\
        .order_by(desc(Prediction.prediction_date))\
        .first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="예측 데이터가 없습니다")
    
    # 방향 텍스트 변환
    direction_map = {
        "UP": "상승 예상",
        "DOWN": "하락 예상",
        "HOLD": "보합 예상"
    }
    
    # 신뢰도 계산
    confidence_percent = int(prediction.confidence * 100) if prediction.confidence <= 1 else int(prediction.confidence)
    confidence_stars = min(5, max(1, int(confidence_percent / 20)))
    
    # key_factors, risk_factors 처리
    key_factors = prediction.key_factors if isinstance(prediction.key_factors, list) else []
    risk_factors = prediction.risk_factors if isinstance(prediction.risk_factors, list) else []
    
    return TodayPredictionResponse(
        date=prediction.prediction_date.strftime("%Y년 %m월 %d일"),
        direction=prediction.direction,
        direction_text=direction_map.get(prediction.direction, prediction.direction),
        confidence=prediction.confidence,
        confidence_percent=confidence_percent,
        confidence_stars=confidence_stars,
        summary=prediction.summary or "예측 요약이 없습니다.",
        key_factors=key_factors,  # 전체 반환
        risk_factors=risk_factors  # 전체 반환
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


# ============================================
# 월간 시장 흐름 API (이번 달 시장 흐름)
# ============================================
class WeeklyTrend(BaseModel):
    """주간 트렌드 응답"""
    week_number: int              # 1, 2, 3, 4
    week_label: str               # "1주차", "2주차", "이번주"
    start_date: str               # "2/3"
    end_date: str                 # "2/9"
    direction: str                # "UP", "DOWN", "HOLD"
    direction_text: str           # "상승", "하락", "보합"
    total_change: float           # 주간 총 변동률
    summary: str                  # "금리 안정화로 시장 신뢰 회복"
    is_current_week: bool         # 이번 주 여부


class MonthlyTrendResponse(BaseModel):
    """월간 시장 흐름 응답"""
    month: str                    # "2월"
    weeks: List[WeeklyTrend]


@app.get("/api/market/monthly-trend", response_model=MonthlyTrendResponse)
def get_monthly_trend(db: Session = Depends(get_db)):
    """
    이번 달 시장 흐름 (최근 4주)
    - 각 주의 actual_change를 복리 계산으로 상승/하락/보합 판단
    - 주 단위: 월요일 ~ 일요일
    """
    from datetime import timedelta
    
    today = date.today()
    
    # 이번 주 월요일 찾기 (weekday: 월=0, 화=1, ..., 일=6)
    days_since_monday = today.weekday()
    this_monday = today - timedelta(days=days_since_monday)
    
    weeks_data = []
    
    # 최근 4주 데이터 조회 (이번주 포함)
    for i in range(4):
        # i=0: 3주 전, i=1: 2주 전, i=2: 1주 전, i=3: 이번주
        week_offset = 3 - i
        week_monday = this_monday - timedelta(weeks=week_offset)
        week_sunday = week_monday + timedelta(days=6)
        
        # 해당 주의 예측 데이터 조회 (날짜순 정렬)
        predictions = db.query(Prediction).filter(
            Prediction.prediction_date >= week_monday,
            Prediction.prediction_date <= week_sunday,
            Prediction.actual_change.isnot(None)  # 실제 변동률이 있는 것만
        ).order_by(Prediction.prediction_date).all()
        
        # 주간 총 변동률 계산 (복리 방식)
        # 예: +1%, +2%, -1% → (1.01) * (1.02) * (0.99) = 1.0199 → +1.99%
        cumulative = 1.0
        for p in predictions:
            if p.actual_change is not None:
                cumulative *= (1 + p.actual_change / 100)
        
        total_change = (cumulative - 1) * 100  # 퍼센트로 변환
        
        # 방향 결정 (±0.5% 이내면 보합)
        if total_change > 0.5:
            direction = "UP"
            direction_text = "상승"
        elif total_change < -0.5:
            direction = "DOWN"
            direction_text = "하락"
        else:
            direction = "HOLD"
            direction_text = "보합"
        
        # 이번 주 여부
        is_current_week = (week_offset == 0)
        
        # 주차 라벨
        week_number = i + 1
        week_label = "이번주" if is_current_week else f"{week_number}주차"
        
        # 요약 생성
        if is_current_week:
            # 이번 주는 예측 기반
            latest_prediction = db.query(Prediction)\
                .filter(Prediction.prediction_date >= week_monday)\
                .order_by(desc(Prediction.prediction_date))\
                .first()
            if latest_prediction and latest_prediction.summary:
                # summary에서 첫 문장만 추출
                summary = latest_prediction.summary.split('.')[0] + "."
                if len(summary) > 30:
                    summary = summary[:30] + "..."
            else:
                summary = f"{direction_text} 예상"
            # 이번 주는 예측 방향 사용
            if latest_prediction:
                direction = latest_prediction.direction
                direction_text = "상승 예상" if direction == "UP" else "하락 예상" if direction == "DOWN" else "보합 예상"
        else:
            # 지난 주들은 실제 결과 기반 요약
            if direction == "UP":
                summary = "시장 상승세 기록"
            elif direction == "DOWN":
                summary = "시장 하락세 기록"
            else:
                summary = "시장 보합세 유지"
        
        weeks_data.append(WeeklyTrend(
            week_number=week_number,
            week_label=week_label,
            start_date=week_monday.strftime("%-m/%d"),
            end_date=week_sunday.strftime("%-m/%d"),
            direction=direction,
            direction_text=direction_text,
            total_change=round(total_change, 2),
            summary=summary,
            is_current_week=is_current_week
        ))
    
    return MonthlyTrendResponse(
        month=f"{today.month}월",
        weeks=weeks_data
    )