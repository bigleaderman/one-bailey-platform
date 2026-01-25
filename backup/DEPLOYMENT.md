# OneBailey Platform 배포 가이드

## 📋 목차
1. [로컬 개발 환경](#로컬-개발-환경)
2. [서버 초기 설정](#서버-초기-설정)
3. [자동 배포 (GitHub Actions)](#자동-배포-github-actions)
4. [수동 배포](#수동-배포)
5. [트러블슈팅](#트러블슈팅)

---

## 🖥️ 로컬 개발 환경

### 사전 요구사항
- Docker & Docker Compose 설치
- Git 설치

### 1. 저장소 클론
```bash
git clone https://github.com/bigleaderman/one-bailey-platform.git
cd one-bailey-platform
```

### 2. 로컬에서 실행
```bash
# 개발 환경 실행 (PostgreSQL 포함)
docker-compose -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f

# 중지
docker-compose -f docker-compose.dev.yml down
```

### 3. 접속 확인
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🚀 서버 초기 설정

### 서버 정보
- **IP**: 183.111.67.145
- **SSH Port**: 22302
- **사용자**: root
- **배포 경로**: /fscm/onebailey/platform

### 1. 서버 접속
```bash
ssh -p 22302 root@183.111.67.145
```

### 2. Docker 설치
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 설치 확인
docker --version
docker-compose --version
```

### 3. 배포 디렉토리 생성
```bash
mkdir -p /fscm/onebailey/platform
cd /fscm/onebailey/platform
```

### 4. 저장소 클론
```bash
git clone -b dev https://github.com/bigleaderman/one-bailey-platform.git .
```

### 5. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env
nano .env
```

**.env 파일 내용:**
```env
# Database Configuration (기존 postgres-db 컨테이너 정보)
DB_PASSWORD=qlalfdla1234!

# API URLs
NEXT_PUBLIC_API_URL=http://183.111.67.145:8000

# Node Environment
NODE_ENV=production
```

### 6. Let's Encrypt 디렉토리 설정
```bash
# SSL 인증서 디렉토리 생성
mkdir -p letsencrypt
chmod 600 letsencrypt
```

### 7. 초기 배포
```bash
# Docker 이미지 pull
docker pull sosohan/onebaileyplatform:backend-latest
docker pull sosohan/onebaileyplatform:frontend-latest

# 컨테이너 실행
docker-compose up -d

# 상태 확인
docker-compose ps
docker-compose logs -f
```

---

## ⚙️ 자동 배포 (GitHub Actions)

### GitHub Secrets 설정

GitHub 저장소에서 **Settings > Secrets and variables > Actions**로 이동하여 다음 Secrets를 추가:

1. **DOCKER_TOKEN**
   - Docker Hub 접근 토큰
   - Docker Hub > Account Settings > Security > New Access Token

2. **SERVER_SSH_KEY**
   - 서버 SSH 비공개 키 (PEM 형식)
   - `cat ~/.ssh/id_rsa` 또는 사용 중인 SSH 키

### 배포 트리거

**자동 배포 조건:**
- `dev` 또는 `main` 브랜치에 push
- GitHub Actions 수동 실행 (workflow_dispatch)

**배포 과정:**
1. Docker 이미지 빌드 (Backend & Frontend)
2. Docker Hub에 이미지 push
3. 서버에 SSH 접속
4. 최신 코드 pull
5. Docker 이미지 pull
6. 컨테이너 재시작
7. Health Check 및 상태 확인

---

## 🛠️ 수동 배포

### 서버에서 수동 배포

```bash
# 서버 접속
ssh -p 22302 root@183.111.67.145

# 배포 디렉토리로 이동
cd /fscm/onebailey/platform

# 최신 코드 pull
git pull origin dev

# 최신 이미지 pull
docker pull sosohan/onebaileyplatform:backend-latest
docker pull sosohan/onebaileyplatform:frontend-latest

# 컨테이너 재시작
docker-compose down
docker-compose up -d

# 상태 확인
docker-compose ps
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend

# Health Check
curl http://localhost:8000/health
```

### 개별 서비스 재시작

```bash
# Backend만 재시작
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

# Frontend만 재시작
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose up -d frontend

# Traefik만 재시작
docker-compose restart traefik
```

---

## 🔍 모니터링

### 컨테이너 상태 확인
```bash
# 모든 컨테이너 상태
docker-compose ps

# 특정 컨테이너 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f traefik

# 최근 로그만 보기
docker-compose logs --tail=100 backend
```

### Health Check
```bash
# Backend Health Check
curl http://localhost:8000/health

# Frontend 접속 확인
curl -I https://onebailey.shop

# SSL 인증서 확인
curl -vI https://onebailey.shop 2>&1 | grep -i "SSL"
```

### 리소스 사용량
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h

# Docker 이미지/볼륨 정리
docker system prune -a
```

---

## 🐛 트러블슈팅

### 1. Backend가 시작하지 않을 때

**문제:** Backend 컨테이너가 계속 재시작됨

**해결:**
```bash
# 로그 확인
docker-compose logs backend

# DB 연결 확인
docker exec -it postgres-db psql -U admin -d onebailey

# Backend 컨테이너 재생성
docker-compose stop backend
docker-compose rm -f backend
docker pull sosohan/onebaileyplatform:backend-latest
docker-compose up -d backend
```

### 2. Frontend 접속 불가

**문제:** https://onebailey.shop 접속 안 됨

**해결:**
```bash
# Traefik 로그 확인
docker-compose logs traefik

# SSL 인증서 확인
ls -la letsencrypt/

# 80, 443 포트 확인
sudo netstat -tulpn | grep -E ':80|:443'

# Traefik 재시작
docker-compose restart traefik
```

### 3. DB 연결 실패

**문제:** `could not connect to server: Connection refused`

**해결:**
```bash
# postgres-db 컨테이너 확인
docker ps | grep postgres-db

# 네트워크 확인
docker network ls
docker network inspect bridge

# Backend를 default 네트워크에 추가
# docker-compose.yml에서 networks 설정 확인
```

### 4. Let's Encrypt SSL 인증서 문제

**문제:** SSL 인증서 발급 실패

**해결:**
```bash
# 도메인 DNS 확인
nslookup onebailey.shop

# 80, 443 포트가 열려있는지 확인
sudo ufw status

# letsencrypt 디렉토리 권한 확인
chmod 600 letsencrypt/

# acme.json 파일 생성
touch letsencrypt/acme.json
chmod 600 letsencrypt/acme.json

# Traefik 재시작
docker-compose restart traefik
```

### 5. Docker 이미지 빌드 실패

**Backend 빌드 실패:**
```bash
# Python 3.12로 변경됨
# build-essential, libpq-dev 설치됨
# 로컬에서 테스트
cd backend
docker build -t test-backend .
```

**Frontend 빌드 실패:**
```bash
# npm install 사용 (package-lock.json 없음)
# --legacy-peer-deps 옵션 사용
# 로컬에서 테스트
cd frontend
docker build -t test-frontend .
```

---

## 📚 주요 파일 설명

### docker-compose.yml (서버용)
- Backend, Frontend, Traefik 컨테이너 정의
- 기존 postgres-db 컨테이너 연결
- Traefik으로 SSL/TLS 자동 처리
- onebailey.shop 도메인 연결

### docker-compose.dev.yml (로컬용)
- PostgreSQL 컨테이너 포함
- 개발용 설정 (포트 직접 노출)
- 볼륨 마운트로 핫 리로드 지원

### .github/workflows/deploy.yml
- Docker 이미지 자동 빌드
- Docker Hub에 push
- 서버 자동 배포
- Health Check 및 로그 확인

---

## 🔗 주요 URL

- **Frontend**: https://onebailey.shop
- **Backend API**: http://183.111.67.145:8000
- **API 문서**: http://183.111.67.145:8000/docs
- **Docker Hub**: https://hub.docker.com/r/sosohan/onebaileyplatform
- **GitHub**: https://github.com/bigleaderman/one-bailey-platform

---

## 📞 지원

문제가 발생하면:
1. 로그 확인: `docker-compose logs -f`
2. 컨테이너 상태: `docker-compose ps`
3. Health Check: `curl http://localhost:8000/health`
4. GitHub Issues에 문의
