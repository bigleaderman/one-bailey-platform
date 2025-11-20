from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import date
import json
from decimal import Decimal
from app.db import get_db
from app.models import Prediction
from app.services.prediction_service import calculate_market_expectation, calculate_nasdaq_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])

def pred_to_dict(pred):
    """Prediction 모델을 딕셔너리로 변환"""
    return {
        "id": pred.id,
        "prediction_date": str(pred.prediction_date),
        "direction": pred.direction,
        "confidence": float(pred.confidence),
        "actual_direction": pred.actual_direction,
        "actual_change": float(pred.actual_change) if pred.actual_change else None,
        "key_factors": pred.key_factors or [],
        "risk_factors": pred.risk_factors or [],
        "summary": pred.summary,
        "llm_response": pred.llm_response,
        "created_at": pred.created_at.isoformat() if pred.created_at else None,
    }

@router.get("/today")
def get_today_prediction(db: Session = Depends(get_db)):
    """오늘 예측 조회"""
    pred = calculate_market_expectation(db)
    if not pred:
        raise HTTPException(status_code=404, detail="No prediction for today")
    return JSONResponse(
        content=pred_to_dict(pred),
        media_type="application/json; charset=utf-8"
    )

@router.get("/nasdaq")
def get_nasdaq_prediction(db: Session = Depends(get_db)):
    """나스닥 QQQ 예측 조회"""
    preds = calculate_nasdaq_prediction(db)
    if not preds:
        raise HTTPException(status_code=404, detail="No nasdaq prediction")
    preds_list = [pred_to_dict(pred) for pred in preds]
    return JSONResponse(
        content=preds_list,
        media_type="application/json; charset=utf-8"
    )

@router.get("/")
def get_all_predictions(db: Session = Depends(get_db)):
    """모든 예측 조회"""
    preds = db.query(Prediction).all()
    preds_list = [pred_to_dict(pred) for pred in preds]
    return JSONResponse(
        content=preds_list,
        media_type="application/json; charset=utf-8"
    )