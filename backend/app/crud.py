from sqlalchemy.orm import Session
from datetime import date
from . import models, schemas

def get_predictions(db: Session, skip: int = 0, limit: int = 100):
    """모든 예측 조회"""
    return db.query(models.Prediction).offset(skip).limit(limit).all()

def get_prediction_by_date(db: Session, prediction_date: date):
    """특정 날짜의 예측 조회"""
    return db.query(models.Prediction).filter(
        models.Prediction.prediction_date == prediction_date
    ).first()

def create_prediction(db: Session, prediction: schemas.PredictionCreate):
    """새 예측 생성"""
    db_prediction = models.Prediction(**prediction.dict())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def update_prediction(db: Session, prediction_date: date, prediction: schemas.PredictionCreate):
    """예측 업데이트"""
    db_prediction = get_prediction_by_date(db, prediction_date)
    if not db_prediction:
        return None
    for key, value in prediction.dict().items():
        setattr(db_prediction, key, value)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def delete_prediction(db: Session, prediction_date: date):
    """예측 삭제"""
    db_prediction = get_prediction_by_date(db, prediction_date)
    if db_prediction:
        db.delete(db_prediction)
        db.commit()
    return db_prediction