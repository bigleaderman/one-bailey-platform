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

from datetime import datetime, timedelta

# Mock 데이터 생성 함수 (개발용 - 동적으로 최신 날짜 사용)
def get_mock_prediction():
    today = datetime.now()
    return {
        "id": 1,
        "prediction_date": today.strftime("%Y-%m-%d"),
        "direction": "UP",
        "confidence": 0.80,
        "actual_direction": None,
        "actual_change": None,
        "key_factors": [
            "나스닥 선물 및 반도체 지수 강세: NQ 선물이 1.51%, SOX 지수가 1.82% 상승하며 기술주 투자 심리 개선을 시사.",
            "정상적인 금리 스프레드: 2-10년물 금리 스프레드가 양수를 유지하며 경기 침체 우려 완화.",
            "M2 통화량 증가: 통화량 증가로 유동성 개선 기대감 상승."
        ],
        "risk_factors": [
            "높은 VIX 수준: VIX 지수가 20.96으로 중립 수준이지만, 여전히 변동성이 존재하며 예상치 못한 하락 가능성 존재.",
            "달러 강세: 달러 인덱스 상승으로 해외 투자 자금 이탈 가능성.",
            "낮은 풋/콜 비율: 시장 과열 신호로 단기 조정 가능성."
        ],
        "summary": "금리 동결 기대감으로 투자자들의 심리가 좋아졌어요",
        "created_at": today.isoformat()
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
    """최신 예측 조회"""

    # 환경변수로 실제 DB 사용 여부 결정
    use_real_db = os.getenv('USE_REAL_DB', 'false').lower() == 'true'

    if not use_real_db:
        print("⚠️  Using MOCK data (USE_REAL_DB=false)")
        mock_data = get_mock_prediction()
        mock_data['_data_source'] = 'mock'  # 데이터 소스 표시
        return mock_data

    print("🔍 Fetching from REAL database (USE_REAL_DB=true)")
    
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
            print("⚠️  No data found in database, using mock data")
            mock_data = get_mock_prediction()
            mock_data['_data_source'] = 'mock_fallback'
            return mock_data

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

        prediction['_data_source'] = 'database'  # 실제 DB 데이터 표시
        print(f"✅ Fetched from database: {prediction['prediction_date']}, direction={prediction['direction']}")

        return prediction

    except Exception as e:
        print(f"❌ Database error: {e}")
        print(f"Using mock data as fallback")
        mock_data = get_mock_prediction()
        mock_data['_data_source'] = 'mock_error_fallback'
        return mock_data

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
