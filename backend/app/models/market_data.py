"""
시장 데이터 모델
"""
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class MarketData(Base):
    """
    일일 시장 데이터 테이블
    - Yahoo Finance, FRED에서 수집한 시장 지표
    """
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, unique=True)
    
    # 주요 지수
    qqq_price = Column(Float, nullable=True)
    qqq_volume = Column(Float, nullable=True)
    vix_level = Column(Float, nullable=True)
    
    # 선물/지수
    nq_future = Column(Float, nullable=True)
    nq_change = Column(Float, nullable=True)
    sox_index = Column(Float, nullable=True)
    sox_change = Column(Float, nullable=True)
    
    # 달러/금리
    dxy_level = Column(Float, nullable=True)
    dxy_change = Column(Float, nullable=True)
    treasury_10y = Column(Float, nullable=True)
    treasury_2y = Column(Float, nullable=True)
    spread_2_10y = Column(Float, nullable=True)
    fed_funds_rate = Column(Float, nullable=True)
    
    # 원자재
    wti_oil = Column(Float, nullable=True)
    gold_price = Column(Float, nullable=True)

    # 메타데이터
    collection_meta = Column(JSONB, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
