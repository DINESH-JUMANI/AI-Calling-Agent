#!/bin/bash

# Production deployment script

echo "Deploying AI Call Assistant..."

# Pull latest code
git pull origin main

# Build and start containers
docker-compose down
docker-compose up --build -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Check health
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment completed successfully!"