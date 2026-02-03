#!/bin/bash

# Local Development Setup
# This script starts the entire stack using Docker Compose for local development

echo "Starting Supermarket Application Stack (Docker Compose)..."
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# Stop and remove existing containers
echo "Cleaning up previous containers..."
docker-compose down --remove-orphans || true

# Build images first
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

echo ""
echo "================================"
echo "Stack is up and running!"
echo "================================"
echo ""
echo "Service URLs:"
echo "  - UI: http://localhost:5002"
echo "  - BFF API: http://localhost:5000"
echo "  - Core Service API: http://localhost:5001"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
