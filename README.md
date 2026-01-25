# OneBailey Platform

미국 증시(QQQ ETF) 예측 서비스

## 📋 프로젝트 구조
 
``` 
one-bailey-platform/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       └── main.py           # FastAPI 앱 (DB 연동)
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docker-compose.yml        # 로컬 개발용
├── test_api.py               # API 테스트 스크립트
└── README.md
```

---

## 🚀 로컬 실행 방법

### 1. 사전 요구사항
- Docker & Docker Compose
- Python 3.x (테스트용)

### 2. 실행

```bash
# 빌드 및 실행
docker compose up -d --build

# 프론트엔드 캐시 문제 시 (403 에러)
docker compose build --no-cache frontend
docker compose up -d
```

### 3. 접속 확인
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 4. 종료

```bash
docker compose down
```

---

## 🧪 API 테스트

### Python 스크립트로 테스트

```bash
# requests 설치 (없으면)
pip install requests

# 테스트 실행
python test_api.py
```

### curl로 테스트

```bash
# 헬스체크
curl http://localhost:8000/

# 오늘의 예측
curl http://localhost:8000/api/predictions/today

# 예측 목록
curl http://localhost:8000/api/predictions?limit=5
```

### 브라우저에서 테스트
- http://localhost:8000/docs (Swagger UI)

---

## 📡 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 상태 확인 |
| GET | `/health` | 헬스체크 |
| GET | `/api/predictions/today` | 오늘의 예측 |
| GET | `/api/predictions` | 예측 목록 (limit, skip 파라미터) |
| GET | `/api/predictions/{id}` | 특정 예측 조회 |

### 응답 예시 (`/api/predictions/today`)

```json
{
  "date": "2025년 01월 25일",
  "direction": "UP",
  "direction_text": "상승 예상",
  "confidence": 0.75,
  "confidence_percent": 75,
  "confidence_stars": 4,
  "summary": "금리 동결 기대감으로 투자자들의 심리가 좋아졌어요",
  "key_factors": ["나스닥 선물 강세", "금리 안정화"],
  "risk_factors": ["VIX 변동성", "달러 강세"]
}
```

---

## 🗄️ 데이터베이스

### 연결 정보 (서버 DB)
| 항목 | 값 |
|------|-----|
| Host | 183.111.67.145 |
| Port | 5432 |
| Database | onebailey |
| User | admin |

### predictions 테이블 스키마

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | PK |
| prediction_date | DATE | 예측 날짜 |
| direction | VARCHAR(10) | UP/DOWN/HOLD |
| confidence | FLOAT | 신뢰도 (0.0~1.0) |
| actual_direction | VARCHAR(10) | 실제 결과 |
| actual_change | FLOAT | 실제 변동률 |
| key_factors | JSON | 상승 요인 리스트 |
| risk_factors | JSON | 리스크 요인 리스트 |
| summary | TEXT | 예측 요약 |
| llm_response | JSON | LLM 원본 응답 |
| created_at | TIMESTAMP | 생성 시간 |

---

## 🔧 트러블슈팅

### 403 Forbidden (Frontend)
```bash
# 파일 권한 문제 - 캐시 없이 재빌드
docker compose build --no-cache frontend
docker compose up -d

# 또는 직접 권한 수정
docker exec onebailey-frontend chmod 644 /usr/share/nginx/html/*
```

### DB 연결 실패
```bash
# 백엔드 로그 확인
docker logs onebailey-backend --tail 50

# DB 연결 테스트
docker run --rm postgres:15-alpine psql "postgresql://admin:PASSWORD@183.111.67.145:5432/onebailey" -c "SELECT 1;"
```

### 컨테이너 상태 확인
```bash
docker compose ps
docker compose logs -f
```

### 전체 재시작
```bash
docker compose down
docker compose up -d --build
```

---

## 🌐 서버 배포 정보

### 서버
| 항목 | 값 |
|------|-----|
| IP | 183.111.67.145 |
| SSH Port | 22302 |
| User | root |
| Backend 경로 | /fscm/onebailey/backend |
| Frontend 경로 | /fscm/onebailey/frontend |

### Docker Hub
- Repository: `sosohan/onebaileyplatform`
- Tags: `backend-latest`, `frontend-latest`

### GitHub Actions
- dev/main 브랜치 push 시 자동 배포
- Secrets 필요: `DOCKER_TOKEN`, `SERVER_SSH_KEY`

---

## 📱 프론트엔드 기능

- ✅ 오늘의 시장 예측 표시 (상승/하락/보합)
- ✅ 신뢰도 별점 표시
- ✅ 예측 근거 보기 (확장/축소)
- ✅ 상승 요인 / 리스크 요인 목록
- ⬜ 알림 기능 (준비 중)
- ⬜ 상세 분석 페이지 (준비 중)

---

## 📝 개발 참고

### 기술 스택
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, psycopg2
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Database**: PostgreSQL 15
- **Infra**: Docker, Nginx, GitHub Actions

### 로컬 개발 시 주의사항
- docker-compose.yml의 DB 비밀번호는 Git에 커밋하지 않도록 주의
- 서버 DB에 직접 연결하므로 데이터 변경 시 주의

---

© 2025 OneBailey. All rights reserved.
