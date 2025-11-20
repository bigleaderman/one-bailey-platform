# OneBailey Frontend

Next.js 15 + TypeScript 기반 프론트엔드

## 개발

```bash
npm install
npm run dev
```

http://localhost:3000

## 빌드

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t sosohan/onebailey-frontend:latest .
docker push sosohan/onebailey-frontend:latest
```

## 환경변수

- `NEXT_PUBLIC_API_URL`: 백엔드 API URL
