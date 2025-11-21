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
