from sqlalchemy.orm import Session
from datetime import date
from app.models import Prediction

def calculate_market_expectation(db: Session):
    """오늘 예측 1개 반환"""
    today = date.today()
    return db.query(Prediction).filter(
        Prediction.prediction_date == today
    ).first()

def calculate_nasdaq_prediction(db: Session):
    """오늘 예측 반환 (nasdaq 이름이지만 동일 데이터)"""
    today = date.today()
    return db.query(Prediction).filter(
        Prediction.prediction_date == today
    ).all()