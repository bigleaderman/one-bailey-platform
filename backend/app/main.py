from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.routers import predictions

# 테이블 자동생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OneBailey API",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터
app.include_router(predictions.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}