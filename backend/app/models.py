from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.db import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(Date, nullable=False, unique=True)  # 하루에 1개만
    direction = Column(String(10), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    actual_direction = Column(String(10), nullable=True)
    actual_change = Column(Numeric(5, 2), nullable=True)
    key_factors = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    summary = Column(String, nullable=True)
    llm_response = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("direction IN ('UP', 'DOWN')"),
        CheckConstraint("confidence >= 0.5 AND confidence <= 0.99"),
    )