# OneBailey - 로컬 테스트 가이드

## 📁 파일 구조

```
one-bailey-platform/
├── backend/
│   ├── Dockerfile              ← 새로 교체
│   ├── requirements.txt        ← 새로 교체
│   └── app/
│       ├── __init__.py         ← 새로 추가
│       └── main.py             ← 새로 교체
├── frontend/
│   ├── Dockerfile              ← 새로 교체
│   ├── nginx.conf              ← 새로 추가
│   ├── index.html              ← 새로 교체
│   ├── styles.css              ← 새로 교체
│   └── app.js                  ← 새로 교체
└── docker-compose.yml          ← 새로 교체
```

## 🚀 로컬 실행 방법

### 1. 파일 교체
다운로드한 파일들을 저장소에 복사하세요.

### 2. 실행
```bash
# 저장소 루트에서
cd /path/to/one-bailey-platform

# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### 3. 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 4. 종료
```bash
docker-compose down
```

## 🔧 문제 해결

### DB 연결 오류
```bash
# DB 컨테이너 상태 확인
docker logs postgres-db

# DB 수동 연결 테스트
docker exec -it postgres-db psql -U admin -d onebailey
```

### Backend 오류
```bash
# 로그 확인
docker logs onebailey-backend

# 컨테이너 내부 접속
docker exec -it onebailey-backend /bin/sh
```

### 빌드 오류
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 전체 정리 후 재시작
docker-compose down -v
docker-compose up -d --build
```

## 📝 테스트 데이터 삽입

DB에 테스트 데이터가 없으면:

```bash
docker exec -it postgres-db psql -U admin -d onebailey -c "
INSERT INTO predictions (prediction_date, direction, confidence, summary, key_factors, risk_factors)
VALUES (
    CURRENT_DATE,
    'UP',
    0.75,
    '금리 동결 기대감으로 투자자들의 심리가 좋아졌어요',
    '[\"나스닥 선물 강세\", \"금리 안정화 기대\", \"기술주 실적 호조\"]',
    '[\"VIX 변동성 주의\", \"달러 강세 우려\"]'
);
"
```

## ✅ 체크리스트

- [ ] docker-compose up 성공
- [ ] http://localhost:3000 접속 가능
- [ ] http://localhost:8000 접속 가능
- [ ] 프론트엔드에서 데이터 표시됨
