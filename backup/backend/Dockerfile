FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치 (psycopg2-binary 빌드에 필요)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
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

# Uvicorn으로 실행 (프로덕션 환경)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
