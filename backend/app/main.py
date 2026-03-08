"""
OneBailey Backend - FastAPI Application
메인 엔트리포인트
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import predictions_router, market_router


# ============================================
# FastAPI App 생성
# ============================================
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# ============================================
# CORS 설정
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 라우터 등록
# ============================================
app.include_router(predictions_router)
app.include_router(market_router)


# ============================================
# 기본 엔드포인트
# ============================================
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"status": "ok", "message": "OneBailey API is running"}


@app.get("/health")
async def health():
    """헬스체크"""
    return {"status": "healthy"}
