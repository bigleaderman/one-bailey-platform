"""
예측 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.prediction import (
    TodayPredictionResponse,
    PredictionResponse,
    PredictionHistoryResponse
)
from app.services.prediction_service import PredictionService


router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/today", response_model=TodayPredictionResponse)
def get_today_prediction(db: Session = Depends(get_db)):
    """오늘의 예측 조회"""
    result = PredictionService.get_today_prediction(db)
    if not result:
        raise HTTPException(status_code=404, detail="예측 데이터가 없습니다")
    return result


@router.get("/history", response_model=PredictionHistoryResponse)
def get_prediction_history(days: int = 7, db: Session = Depends(get_db)):
    """최근 예측 기록 + 적중률"""
    return PredictionService.get_prediction_history(db, days)


@router.get("", response_model=List[PredictionResponse])
def get_predictions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """예측 목록 조회"""
    return PredictionService.get_predictions(db, skip, limit)


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """특정 예측 조회"""
    result = PredictionService.get_prediction_by_id(db, prediction_id)
    if not result:
        raise HTTPException(status_code=404, detail="예측을 찾을 수 없습니다")
    return result
