#!/bin/bash

###############################################################################
# OneBailey Platform Deployment Script
# Usage: ./deploy.sh [dev|prod]
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Environment (dev or prod)
ENV=${1:-prod}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OneBailey Platform Deployment${NC}"
echo -e "${GREEN}Environment: ${ENV}${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        if [ -f .env.example ]; then
            cp .env.example .env
            echo -e "${GREEN}.env file created. Please edit it with your values.${NC}"
            exit 1
        else
            echo -e "${RED}Error: .env.example not found${NC}"
            exit 1
        fi
    fi
}

# Function to pull latest images
pull_images() {
    echo -e "\n${GREEN}Pulling latest Docker images...${NC}"
    docker pull sosohan/onebaileyplatform:backend-latest
    docker pull sosohan/onebaileyplatform:frontend-latest
    docker pull postgres:16-alpine
    docker pull nginx:alpine
}

# Function to deploy
deploy() {
    local compose_file=$1

    echo -e "\n${GREEN}Deploying with ${compose_file}...${NC}"

    # Stop existing containers
    echo -e "${YELLOW}Stopping existing containers...${NC}"
    docker-compose -f ${compose_file} down

    # Start new containers
    echo -e "${GREEN}Starting containers...${NC}"
    docker-compose -f ${compose_file} up -d

    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 10

    # Check service health
    echo -e "\n${GREEN}Checking service health...${NC}"
    docker-compose -f ${compose_file} ps
}

# Function to cleanup
cleanup() {
    echo -e "\n${GREEN}Cleaning up unused Docker resources...${NC}"
    docker image prune -af
    docker volume prune -f
}

# Function to show logs
show_logs() {
    local compose_file=$1
    echo -e "\n${GREEN}Service logs:${NC}"
    docker-compose -f ${compose_file} logs --tail=50
}

# Main deployment flow
main() {
    if [ "$ENV" == "prod" ]; then
        check_env_file
        pull_images
        deploy "docker-compose.prod.yml"
        cleanup

        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}Production Deployment Complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "Frontend: http://onebailey.shop"
        echo -e "Backend: http://onebailey.shop/api"
        echo -e "Health: http://onebailey.shop/health"

    elif [ "$ENV" == "dev" ]; then
        deploy "docker-compose.yml"

        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}Development Deployment Complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "Frontend: http://localhost:3000"
        echo -e "Backend: http://localhost:8000"
        echo -e "Health: http://localhost:8000/health"

    else
        echo -e "${RED}Error: Invalid environment. Use 'dev' or 'prod'${NC}"
        echo -e "Usage: ./deploy.sh [dev|prod]"
        exit 1
    fi

    # Show recent logs
    if [ "$ENV" == "prod" ]; then
        show_logs "docker-compose.prod.yml"
    else
        show_logs "docker-compose.yml"
    fi
}

# Run main function
main
