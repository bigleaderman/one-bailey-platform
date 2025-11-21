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
