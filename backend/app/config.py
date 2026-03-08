"""
환경 설정
- DB 연결 정보
- 앱 설정
"""
import os


class Settings:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "postgres-db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "onebailey")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # App
    APP_TITLE: str = "OneBailey API"
    APP_DESCRIPTION: str = "QQQ ETF 예측 서비스 API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
