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
        key_factors=key_factors[:5] if key_factors else [],
        risk_factors=risk_factors[:5] if risk_factors else []
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
