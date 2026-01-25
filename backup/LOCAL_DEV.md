# 로컬 개발 환경 가이드

## 개요

로컬 개발 환경은 서버의 실제 PostgreSQL 데이터베이스에 연결하여 실제 데이터를 사용합니다.

## 아키텍처

```
로컬 환경:
├── Backend (localhost:8000) ──→ 서버 DB (183.111.67.145:5432)
└── Frontend (localhost:3000) ──→ 로컬 Backend (localhost:8000)
```

## 사전 요구사항

### 1. 서버 PostgreSQL 접근 허용 설정

서버의 PostgreSQL이 외부 IP에서 접근을 허용하도록 설정되어야 합니다:

**서버에서 실행:**
```bash
# PostgreSQL 컨테이너 접속
docker exec -it postgres-db bash

# pg_hba.conf 수정
vi /var/lib/postgresql/data/pg_hba.conf

# 다음 라인 추가 (개발용 - 프로덕션에서는 특정 IP만 허용)
host    all             all             0.0.0.0/0               md5

# PostgreSQL 재시작
docker restart postgres-db
```

**postgresql.conf 확인:**
```bash
# listen_addresses가 '*' 또는 '0.0.0.0'으로 설정되어야 함
docker exec -it postgres-db psql -U admin -d onebailey -c "SHOW listen_addresses;"
```

### 2. 방화벽 설정 (서버)

PostgreSQL 포트(5432)가 열려 있어야 합니다:
```bash
# 포트 확인
sudo ufw status

# 필요시 포트 열기
sudo ufw allow 5432/tcp
```

## 로컬 개발 시작

### 1. Docker Compose로 시작
```bash
# 컨테이너 빌드 및 시작
docker-compose -f docker-compose.dev.yml up --build

# 백그라운드로 실행
docker-compose -f docker-compose.dev.yml up -d --build
```

### 2. 접속 확인

**Backend:**
- http://localhost:8000
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/api/predictions/latest

**Frontend:**
- http://localhost:3000

### 3. 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.dev.yml logs -f

# Backend 로그만
docker-compose -f docker-compose.dev.yml logs -f backend

# Frontend 로그만
docker-compose -f docker-compose.dev.yml logs -f frontend
```

## 핫 리로드 (Hot Reload)

### Backend
- `./backend/app` 디렉토리의 변경사항이 자동으로 반영됩니다
- Uvicorn의 `--reload` 옵션 사용

### Frontend
- Next.js 개발 서버가 파일 변경을 자동 감지합니다
- 브라우저가 자동으로 새로고침됩니다

## 데이터 소스 확인

Backend API 응답에 `_data_source` 필드가 포함되어 데이터 출처를 확인할 수 있습니다:

- `database`: 서버의 실제 PostgreSQL 데이터
- `mock`: Mock 데이터 (USE_REAL_DB=false일 때)
- `mock_fallback`: DB에 데이터가 없을 때 fallback
- `mock_error_fallback`: DB 연결 오류 시 fallback

## 문제 해결

### Backend가 서버 DB에 연결되지 않는 경우

1. **서버 DB 컨테이너 확인:**
   ```bash
   ssh -p 22302 root@183.111.67.145
   docker ps | grep postgres-db
   docker logs postgres-db
   ```

2. **연결 테스트:**
   ```bash
   # 로컬에서 직접 연결 테스트
   psql -h 183.111.67.145 -p 5432 -U admin -d onebailey
   # 비밀번호: qlalfdla1234!
   ```

3. **Backend 로그 확인:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs backend
   ```
   - `🔍 Fetching from REAL database` 메시지가 보여야 함
   - `✅ Fetched from database` 성공 메시지 확인

### Frontend가 Backend와 통신되지 않는 경우

1. **Backend API 직접 호출:**
   ```bash
   curl http://localhost:8000/api/predictions/latest
   ```

2. **브라우저 개발자 도구 확인:**
   - Network 탭에서 API 요청 상태 확인
   - Console 탭에서 `🔍 Fetching from:` 로그 확인

## 환경 변수

### Backend (docker-compose.dev.yml)
- `DB_HOST`: 183.111.67.145 (서버 IP)
- `DB_PORT`: 5432
- `DB_NAME`: onebailey
- `DB_USER`: admin
- `DB_PASSWORD`: qlalfdla1234!
- `USE_REAL_DB`: "true"

### Frontend (docker-compose.dev.yml)
- `NEXT_PUBLIC_API_URL`: http://localhost:8000
- `NODE_ENV`: development

## 종료

```bash
# 컨테이너 중지
docker-compose -f docker-compose.dev.yml down

# 컨테이너 중지 및 볼륨 삭제
docker-compose -f docker-compose.dev.yml down -v
```
