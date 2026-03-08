"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings


# SQLAlchemy 엔진 생성
engine = create_engine(settings.DATABASE_URL)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스 클래스
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    DB 세션 의존성
    - 요청마다 새 세션 생성
    - 요청 완료 후 자동 종료
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
