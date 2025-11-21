from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

app = FastAPI(
    title="OneBailey API",
    description="QQQ ETF 예측 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock 데이터 (개발용)
MOCK_PREDICTION = {
    "id": 1,
    "prediction_date": "2025-11-20",
    "direction": "UP",
    "confidence": 0.80,
    "actual_direction": None,
    "actual_change": None,
    "key_factors": [
        "나스닥 선물 강세",
        "달러 약세로 위험자산 선호",
        "양의 2-10 스프레드 유지"
    ],
    "risk_factors": [
        "높은 VIX 수준",
        "반도체 섹터 부진"
    ],
    "summary": "글린 통걸 기대감으로 투자자들의 심리가 좋아졌어요",
    "created_at": "2025-11-20T09:00:00"
}

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "OneBailey API",
        "version": "1.0.0",
        "mode": "development",
        "endpoints": [
            "/api/predictions/latest",
            "/api/predictions/stats/accuracy"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "mode": "development"}

@app.get("/api/predictions/latest")
def get_latest_prediction():
    """최신 예측 조회 (개발 모드 - Mock 데이터)"""
    
    # 환경변수로 실제 DB 사용 여부 결정
    use_real_db = os.getenv('USE_REAL_DB', 'false').lower() == 'true'
    
    if not use_real_db:
        return MOCK_PREDICTION
    
    # 실제 DB 연결 (프로덕션)
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import json
        
        DB_CONFIG = {
            'host': os.getenv('DB_HOST', 'postgres-db'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'onebailey'),
            'user': os.getenv('DB_USER', 'admin'),
            'password': os.getenv('DB_PASSWORD', 'qlalfdla1234!')
        }
        
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                id,
                prediction_date,
                direction,
                confidence,
                actual_direction,
                actual_change,
                key_factors,
                risk_factors,
                summary,
                created_at
            FROM predictions
            ORDER BY prediction_date DESC
            LIMIT 1
        """)
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return MOCK_PREDICTION
        
        prediction = dict(result)
        
        # JSONB 필드 파싱
        if prediction.get('key_factors'):
            if isinstance(prediction['key_factors'], str):
                prediction['key_factors'] = json.loads(prediction['key_factors'])
        
        if prediction.get('risk_factors'):
            if isinstance(prediction['risk_factors'], str):
                prediction['risk_factors'] = json.loads(prediction['risk_factors'])
        
        # 날짜 형식 변환
        if prediction.get('prediction_date'):
            prediction['prediction_date'] = str(prediction['prediction_date'])
        if prediction.get('created_at'):
            prediction['created_at'] = prediction['created_at'].isoformat()
        
        return prediction
        
    except Exception as e:
        print(f"Database error: {e}")
        return MOCK_PREDICTION

@app.get("/api/predictions/stats/accuracy")
def get_accuracy_stats():
    """예측 정확도 통계"""
    return {
        "total": 10,
        "correct": 8,
        "accuracy": 80.0,
        "avg_confidence": 0.75
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
