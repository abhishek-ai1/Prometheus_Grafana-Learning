#!/bin/bash

# Build Docker Images for Supermarket Microservices
# This script builds all service images required for deployment

set -e

echo "Building Docker images for Supermarket Application..."

# Build BFF Service
echo "Building BFF Service..."
docker build -t supermarket/bff:latest ./services/bff

# Build Core Service
echo "Building Core Service..."
docker build -t supermarket/core-service:latest ./services/core-service

# Build UI Service
echo "Building UI Service..."
docker build -t supermarket/ui-service:latest ./services/ui-service

echo "All images built successfully!"
echo ""
echo "Images created:"
docker images | grep supermarket || echo "No supermarket images found"
