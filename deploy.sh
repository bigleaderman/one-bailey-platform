#!/bin/bash

# OneBailey Platform 배포 설정 자동화 스크립트

set -e

echo "🚀 OneBailey Platform 배포 설정 시작..."
echo ""

# 프로젝트 루트 확인
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
  echo "❌ 프로젝트 루트에서 실행해주세요"
  echo "현재 위치: $(pwd)"
  exit 1
fi

# 1. Backend Dockerfile
echo "📝 Backend Dockerfile 생성..."
cat > backend/Dockerfile << 'EOF'
FROM python:3.13-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./app /app/app

# 환경변수 설정
ENV PYTHONUNBUFFERED=1
ENV USE_REAL_DB=true

EXPOSE 8000

# Uvicorn으로 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 2. Frontend Dockerfile
echo "📝 Frontend Dockerfile 생성..."
cat > frontend/Dockerfile << 'EOF'
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# 패키지 설치
COPY package*.json ./
RUN npm ci

# 소스 복사 및 빌드
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 비root 유저 생성
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 빌드된 파일 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
EOF

# 3. docker-compose.yml (루트)
echo "📝 docker-compose.yml 생성..."
cat > docker-compose.yml << 'EOF'
services:
  # Backend API
  backend:
    image: sosohan/onebaileyplatform:backend-latest
    container_name: onebailey-backend
    restart: unless-stopped
    environment:
      DB_HOST: postgres-db
      DB_PORT: 5432
      DB_NAME: onebailey
      DB_USER: admin
      DB_PASSWORD: qlalfdla1234!
      USE_REAL_DB: "true"
    ports:
      - "8000:8000"
    networks:
      - onebailey-network

  # Frontend
  frontend:
    image: sosohan/onebaileyplatform:frontend-latest
    container_name: onebailey-frontend
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: http://183.111.67.145:8000
      NODE_ENV: production
    networks:
      - onebailey-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(\`onebailey.shop\`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

  # Traefik (Reverse Proxy + SSL)
  traefik:
    image: traefik:v2.10
    container_name: onebailey-traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./traefik:/etc/traefik"
      - "./letsencrypt:/letsencrypt"
    networks:
      - onebailey-network
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@onebailey.shop"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--entrypoints.web.http.redirections.entryPoint.scheme=https"

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: onebailey
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: qlalfdla1234!
      TZ: Asia/Seoul
    ports:
      - "5432:5432"
    volumes:
      - /fsdata/postgres_data:/var/lib/postgresql/data
    networks:
      - onebailey-network

networks:
  onebailey-network:
    driver: bridge
EOF

# 4. GitHub Actions 디렉토리 생성
echo "📁 GitHub Actions 디렉토리 생성..."
mkdir -p .github/workflows

# 5. Backend 배포 워크플로우
echo "📝 Backend 배포 워크플로우 생성..."
cat > .github/workflows/deploy-backend.yml << 'EOF'
name: Deploy Backend

on:
  push:
    branches: [ dev ]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

env:
  DOCKER_USERNAME: sosohan
  IMAGE_NAME: onebaileyplatform
  SERVER_HOST: 183.111.67.145
  SERVER_USER: root
  SERVER_PORT: 22302

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ env.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_TOKEN }}

    - name: Build and push Backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: |
          ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-latest
          ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-${{ github.sha }}
        cache-from: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-buildcache
        cache-to: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-buildcache,mode=max

    - name: Image info
      run: |
        echo "Backend image pushed:"
        echo "${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-latest"

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ env.SERVER_HOST }}
        username: ${{ env.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: ${{ env.SERVER_PORT }}
        script: |
          cd /fscm/onebailey/platform
          
          # 최신 이미지 pull
          docker pull ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:backend-latest
          
          # Backend 컨테이너만 재시작
          docker compose stop backend
          docker compose rm -f backend
          docker compose up -d backend
          
          # 상태 확인
          sleep 5
          echo "=== Backend Status ==="
          docker compose ps backend
          docker compose logs --tail=30 backend

    - name: Verify Deployment
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ env.SERVER_HOST }}
        username: ${{ env.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: ${{ env.SERVER_PORT }}
        script: |
          cd /fscm/onebailey/platform
          echo "=== Health Check ==="
          curl -f http://localhost:8000/health || echo "Health check failed"
          echo ""
          echo "=== Container Logs ==="
          docker compose logs --tail=20 backend
EOF

# 6. Frontend 배포 워크플로우
echo "📝 Frontend 배포 워크플로우 생성..."
cat > .github/workflows/deploy-frontend.yml << 'EOF'
name: Deploy Frontend

on:
  push:
    branches: [ dev ]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:

env:
  DOCKER_USERNAME: sosohan
  IMAGE_NAME: onebaileyplatform
  SERVER_HOST: 183.111.67.145
  SERVER_USER: root
  SERVER_PORT: 22302

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ env.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_TOKEN }}

    - name: Build and push Frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: |
          ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-latest
          ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-${{ github.sha }}
        cache-from: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-buildcache
        cache-to: type=registry,ref=${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-buildcache,mode=max

    - name: Image info
      run: |
        echo "Frontend image pushed:"
        echo "${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-latest"

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ env.SERVER_HOST }}
        username: ${{ env.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: ${{ env.SERVER_PORT }}
        script: |
          cd /fscm/onebailey/platform
          
          # 최신 이미지 pull
          docker pull ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:frontend-latest
          
          # Frontend 컨테이너만 재시작
          docker compose stop frontend
          docker compose rm -f frontend
          docker compose up -d frontend
          
          # 상태 확인
          sleep 5
          echo "=== Frontend Status ==="
          docker compose ps frontend
          docker compose logs --tail=30 frontend

    - name: Verify Deployment
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ env.SERVER_HOST }}
        username: ${{ env.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        port: ${{ env.SERVER_PORT }}
        script: |
          cd /fscm/onebailey/platform
          echo "=== SSL Certificate Status ==="
          ls -la letsencrypt/ 2>/dev/null || echo "No SSL cert yet"
          echo ""
          echo "=== Frontend Logs ==="
          docker compose logs --tail=20 frontend
          echo ""
          echo "=== Access URL ==="
          echo "Frontend: https://onebailey.shop"
EOF

# 7. 서버 설정 스크립트
echo "📝 서버 설정 스크립트 생성..."
cat > server-setup.sh << 'EOF'
#!/bin/bash

# OneBailey Platform 서버 초기 설정

set -e

echo "🚀 OneBailey Platform 서버 설정 시작..."

# 1. 디렉토리 생성
echo "📁 디렉토리 생성..."
mkdir -p /fscm/onebailey/platform
cd /fscm/onebailey/platform

# 2. docker-compose.yml 다운로드
echo "📥 docker-compose.yml 다운로드..."
curl -o docker-compose.yml https://raw.githubusercontent.com/bigleaderman/one-bailey-platform/dev/docker-compose.yml

# 3. 필수 디렉토리 생성
echo "📁 필수 디렉토리 생성..."
mkdir -p traefik letsencrypt
chmod 600 letsencrypt

# 4. 네트워크 생성
echo "🌐 Docker 네트워크 생성..."
docker network create onebailey-network 2>/dev/null || echo "네트워크 이미 존재"

# 5. 방화벽 설정
echo "🔥 방화벽 설정..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 5432/tcp

# 6. 이미지 pull
echo "📥 Docker 이미지 다운로드..."
docker pull sosohan/onebaileyplatform:backend-latest
docker pull sosohan/onebaileyplatform:frontend-latest

# 7. 컨테이너 시작
echo "🚀 컨테이너 시작..."
docker compose up -d

# 8. 상태 확인
sleep 10
echo ""
echo "✅ 설정 완료!"
echo ""
echo "📊 컨테이너 상태:"
docker compose ps
echo ""
echo "🌐 접속 URL:"
echo "  Frontend: https://onebailey.shop"
echo "  Backend: http://183.111.67.145:8000"
echo "  API Health: http://183.111.67.145:8000/health"
echo ""
echo "📋 로그 확인:"
echo "  docker compose logs -f backend"
echo "  docker compose logs -f frontend"
echo "  docker compose logs -f traefik"
EOF

chmod +x server-setup.sh

# 8. DEPLOYMENT.md
echo "📝 DEPLOYMENT.md 생성..."
cat > DEPLOYMENT.md << 'EOF'
# 🚀 OneBailey Platform 배포 가이드

## 📊 아키텍처

```
onebailey.shop (Frontend)
    ↓ HTTPS (Traefik)
Frontend Container (Next.js)
    ↓ HTTP
Backend Container (FastAPI)
    ↓
PostgreSQL Container
```

## 🔐 GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions:

- `DOCKER_TOKEN`: Docker Hub Access Token
- `SERVER_SSH_KEY`: SSH Private Key 전체 내용

## 🖥️ 서버 초기 설정

```bash
# 서버 접속
ssh -p 22302 root@183.111.67.145

# 스크립트 다운로드 및 실행
curl -o server-setup.sh https://raw.githubusercontent.com/bigleaderman/one-bailey-platform/dev/server-setup.sh
chmod +x server-setup.sh
./server-setup.sh
```

## 🔄 자동 배포

```bash
# Backend 배포
git add backend/
git commit -m "Update backend"
git push origin dev

# Frontend 배포
git add frontend/
git commit -m "Update frontend"
git push origin dev
```

## 🌐 접속 URL

- Frontend: https://onebailey.shop
- Backend: http://183.111.67.145:8000
- API Docs: http://183.111.67.145:8000/docs
EOF

# 9. .dockerignore 파일들
echo "📝 .dockerignore 파일 생성..."

cat > backend/.dockerignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
.git
EOF

cat > frontend/.dockerignore << 'EOF'
node_modules/
.next/
.git
.env.local
EOF

# 완료
echo ""
echo "✅ 배포 설정 완료!"
echo ""
echo "📋 생성된 파일:"
echo "  ✓ backend/Dockerfile"
echo "  ✓ frontend/Dockerfile"
echo "  ✓ docker-compose.yml"
echo "  ✓ .github/workflows/deploy-backend.yml"
echo "  ✓ .github/workflows/deploy-frontend.yml"
echo "  ✓ server-setup.sh"
echo "  ✓ DEPLOYMENT.md"
echo "  ✓ backend/.dockerignore"
echo "  ✓ frontend/.dockerignore"
echo ""
echo "🚀 다음 단계:"
echo "  1. Git 커밋 및 푸시"
echo "     git add ."
echo "     git commit -m 'Add Docker deployment configuration'"
echo "     git push origin dev"
echo ""
echo "  2. GitHub Secrets 설정"
echo "     - DOCKER_TOKEN"
echo "     - SERVER_SSH_KEY"
echo ""
echo "  3. 서버 초기 설정"
echo "     scp -P 22302 server-setup.sh root@183.111.67.145:~"
echo "     ssh -p 22302 root@183.111.67.145 ./server-setup.sh"
echo ""
