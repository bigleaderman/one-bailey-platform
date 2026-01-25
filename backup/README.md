# OneBailey Platform

## Overview
OneBailey is a full-stack web application that provides predictions on the US stock market, specifically focusing on QQQ ETF. The platform features a Next.js frontend and FastAPI backend, designed for containerized deployment.

## Tech Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **UI**: Tailwind CSS
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: PostgreSQL
- **Language**: Python 3.13

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Automated via workflows

## Project Structure

```
one-bailey-platform/
├── .github/
│   └── workflows/
│       ├── deploy-backend.yml      # Backend deployment workflow
│       └── deploy-frontend.yml     # Frontend deployment workflow
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── db.py                   # Database configuration
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── crud.py                 # Database operations
│   │   ├── routers/
│   │   │   └── predictions.py      # Prediction API routes
│   │   ├── services/
│   │   │   └── prediction_service.py  # Prediction business logic
│   │   └── templates/
│   │       └── index.html          # HTML templates
│   ├── Dockerfile                  # Production backend image
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── app/                        # Next.js app directory
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home page
│   │   ├── globals.css             # Global styles
│   │   └── prediction/
│   │       └── [id]/
│   │           └── page.tsx        # Dynamic prediction page
│   ├── lib/
│   │   └── api.ts                  # API client functions
│   ├── Dockerfile                  # Multi-stage frontend build
│   ├── docker-compose.yml          # Frontend development compose
│   ├── next.config.js              # Next.js configuration
│   ├── package.json                # Node dependencies
│   ├── tailwind.config.ts          # Tailwind CSS config
│   └── tsconfig.json               # TypeScript config
├── nginx/
│   └── html/                       # Static HTML files
├── docker-compose.yml              # Main development environment
├── deploy.sh                       # Deployment script
├── server-setup.sh                 # Server initial setup
├── DEPLOYMENT.md                   # Deployment documentation
├── pyproject.toml                  # Python project config
└── README.md                       # This file
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Node.js 20+ (for local frontend development)
- Python 3.13+ (for local backend development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bigleaderman/one-bailey-platform.git
   cd one-bailey-platform
   ```

2. **Start services with Docker Compose**
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

### Development Without Docker

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Initial Server Setup

1. **SSH into your server**
   ```bash
   ssh root@your-server-ip
   ```

2. **Run the setup script**
   ```bash
   chmod +x server-setup.sh
   ./server-setup.sh
   ```

### Automated Deployment (CI/CD)

The project uses GitHub Actions for automated deployment. Workflows are triggered on push to specific branches.

#### GitHub Secrets Required

Configure these secrets in your GitHub repository (Settings > Secrets and variables > Actions):

- `DOCKER_TOKEN`: Docker Hub access token
- `SERVER_SSH_KEY`: SSH private key for server access (PEM format)

### Manual Deployment

```bash
# On your server
cd /root/one-bailey-platform
git pull origin dev

# Deploy
chmod +x deploy.sh
./deploy.sh
```

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
DB_HOST=localhost
DB_PORT=5432
DB_NAME=onebailey
DB_USER=admin
DB_PASSWORD=your_password
USE_REAL_DB=false  # Set to true for production
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Monitoring & Maintenance

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Database Operations
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U admin -d onebailey

# Backup database
docker exec postgres pg_dump -U admin onebailey > backup_$(date +%Y%m%d).sql
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

### Port already in use
```bash
# Find process using the port
lsof -i :8000  # or :3000 for frontend

# Stop the process or change the port in docker-compose.yml
```

## Development Tips

### Hot Reload
- Frontend: Changes in `frontend/` trigger automatic reload
- Backend: Changes in `backend/app/` trigger uvicorn reload (with `--reload` flag)

### Building Docker Images Locally
```bash
# Backend
docker build -t onebailey-backend ./backend

# Frontend
docker build -t onebailey-frontend ./frontend
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer
This application does not provide financial advice and is not responsible for any investment losses. Please consult with a financial advisor before making investment decisions.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
