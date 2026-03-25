"""
예측 데이터 모델
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.database import Base


class Prediction(Base):
    """
    예측 테이블
    - AI가 생성한 일별 QQQ 예측 데이터
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(Date, nullable=False, unique=True)
    direction = Column(String(10), nullable=False)  # UP, DOWN, HOLD
    confidence = Column(Float, nullable=False)
    actual_direction = Column(String(10), nullable=True)
    actual_change = Column(Float, nullable=True)
    key_factors = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    llm_response = Column(JSON, nullable=True)
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
