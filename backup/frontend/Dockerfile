# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# 패키지 설치 (npm install로 변경 - package-lock.json 없음)
COPY package*.json ./
RUN npm install --legacy-peer-deps

# 소스 복사 및 빌드
COPY . .
RUN npm run build

# public 디렉토리 생성 (없을 경우를 대비)
RUN mkdir -p public

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
