# OneBailey Platform

## Overview
OneBailey is a containerized full-stack web application that provides predictions on the US stock market, specifically focusing on QQQ ETF. The platform features a Next.js frontend and FastAPI backend, deployed using Docker containers with automated CI/CD.

🌐 **Live Demo**: [onebailey.shop](https://onebailey.shop)
🐳 **Docker Hub**: [sosohan/onebaileyplatform](https://hub.docker.com/repository/docker/sosohan/onebaileyplatform)

## Tech Stack

### Frontend
- **Framework**: Next.js 15.1.0
- **UI**: React 19, Tailwind CSS
- **Build**: Standalone output for Docker

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn with 4 workers
- **Database**: PostgreSQL 16

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub
- **Domain**: onebailey.shop

## Project Structure

```
one-bailey-platform/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── db.py                   # Database configuration
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── crud.py                 # Database operations
│   │   ├── routers/                # API routes
│   │   ├── services/               # Business logic
│   │   └── templates/              # HTML templates
│   ├── Dockerfile                  # Production backend image
│   ├── .dockerignore
│   └── requirements.txt
├── frontend/
│   ├── app/                        # Next.js app directory
│   ├── public/                     # Static assets
│   ├── Dockerfile                  # Multi-stage frontend build
│   ├── .dockerignore
│   ├── next.config.js              # Next.js configuration
│   └── package.json
├── nginx/
│   ├── nginx.conf                  # Main nginx config
│   ├── conf.d/
│   │   ├── default.conf            # HTTP configuration
│   │   └── onebailey.conf          # HTTPS configuration
│   └── ssl/                        # SSL certificates
├── docker-compose.yml              # Development environment
├── docker-compose.prod.yml         # Production environment
├── deploy.sh                       # Deployment script
├── .env.example                    # Environment template
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bigleaderman/one-bailey-platform.git
   cd one-bailey-platform
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop services**
   ```bash
   docker-compose down
   ```

## Production Deployment

### Initial Setup on VM

1. **SSH into your VM**
   ```bash
   ssh -p 22302 root@183.111.67.145
   ```

2. **Install Docker & Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Clone the repository**
   ```bash
   git clone https://github.com/bigleaderman/one-bailey-platform.git
   cd one-bailey-platform
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual values
   ```

5. **Setup SSL certificates** (optional, for HTTPS)
   ```bash
   # Install certbot
   sudo apt-get update
   sudo apt-get install certbot

   # Get SSL certificate
   sudo certbot certonly --webroot -w ./nginx/html \
     -d onebailey.shop -d www.onebailey.shop

   # Copy certificates
   sudo cp /etc/letsencrypt/live/onebailey.shop/fullchain.pem ./nginx/ssl/
   sudo cp /etc/letsencrypt/live/onebailey.shop/privkey.pem ./nginx/ssl/
   sudo chmod 644 ./nginx/ssl/fullchain.pem
   sudo chmod 600 ./nginx/ssl/privkey.pem
   ```

6. **Deploy**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh prod
   ```

### Automated Deployment (CI/CD)

The project uses GitHub Actions for automated deployment. On every push to `dev` or `main` branches:

1. **Builds** Docker images for frontend and backend
2. **Pushes** images to Docker Hub
3. **Deploys** to VM automatically

#### Required GitHub Secrets

Add these secrets in your GitHub repository settings (Settings > Secrets and variables > Actions):

- `DOCKER_TOKEN`: Your Docker Hub access token
- `SERVER_SSH_KEY`: Your VM SSH private key (PEM format)

**Note**: Server connection details (host, port, username) are configured in the workflow file.

### Manual Deployment

```bash
# On your VM
cd /root/one-bailey-platform

# Pull latest changes
git pull origin main

# Pull latest images
docker pull sosohan/onebaileyplatform:backend-latest
docker pull sosohan/onebaileyplatform:frontend-latest

# Deploy
./deploy.sh prod
```

## Architecture

### Container Overview

```
┌─────────────────┐
│   Nginx Proxy   │  (Port 80/443)
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼────┐ ┌──▼──────┐
│Frontend│ │ Backend │
│:3000   │ │ :8000   │
└────────┘ └────┬────┘
                │
         ┌──────▼──────┐
         │ PostgreSQL  │
         │   :5432     │
         └─────────────┘
```

### Service Communication

- **Frontend** → **Backend**: Internal Docker network
- **Nginx** → **Frontend**: Reverse proxy for `/`
- **Nginx** → **Backend**: Reverse proxy for `/api`
- **Backend** → **PostgreSQL**: Database connection

### Docker Images

Images are automatically built and pushed to Docker Hub:

- `sosohan/onebaileyplatform:frontend-latest`
- `sosohan/onebaileyplatform:frontend-{branch}`
- `sosohan/onebaileyplatform:backend-latest`
- `sosohan/onebaileyplatform:backend-{branch}`

## API Endpoints

### Health & Info
- `GET /` - Service information
- `GET /health` - Health check

### Predictions
- `GET /api/predictions/latest` - Get latest QQQ prediction
- `GET /api/predictions/stats/accuracy` - Get prediction accuracy stats

## Environment Variables

### Backend
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=onebailey
DB_USER=admin
DB_PASSWORD=your_password
USE_REAL_DB=false  # Set to true for production
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://backend:8000
NODE_ENV=production
```

## Monitoring & Maintenance

### Check Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart Services
```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Update Services
```bash
./deploy.sh prod
```

### Database Backup
```bash
docker exec onebailey-postgres pg_dump -U admin onebailey > backup_$(date +%Y%m%d).sql
```

### SSL Certificate Renewal
```bash
sudo certbot renew
sudo cp /etc/letsencrypt/live/onebailey.shop/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/onebailey.shop/privkey.pem ./nginx/ssl/
docker-compose -f docker-compose.prod.yml restart nginx
```

## Development

### Project Setup for Development

1. **Backend Development**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Building Docker Images Locally

```bash
# Backend
docker build -t onebailey-backend ./backend

# Frontend
docker build -t onebailey-frontend ./frontend
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs {service_name}

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Database connection issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify environment variables
docker-compose config
```

### Nginx 502 Bad Gateway
```bash
# Check if backend is running
docker-compose ps backend

# Check nginx configuration
docker-compose exec nginx nginx -t

# Reload nginx
docker-compose restart nginx
```

### SSL certificate issues
```bash
# Verify certificate files exist
ls -la nginx/ssl/

# Check nginx SSL configuration
docker-compose exec nginx cat /etc/nginx/conf.d/onebailey.conf

# Test SSL
curl -vI https://onebailey.shop
```

## Disclaimer
This application does not provide financial advice and is not responsible for any investment losses. Please consult with a financial advisor before making investment decisions.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.