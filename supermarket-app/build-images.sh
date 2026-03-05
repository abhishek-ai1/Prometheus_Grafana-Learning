#!/bin/bash

# Build Docker Images for Supermarket Microservices
# This script builds all service images required for deployment

set -e

echo "Building Docker images for Supermarket Application..."

# allow overriding registry (docker.io/user or local registry)
REGISTRY=${REGISTRY:-"docker.io/abhishekjain2001"}
APP_NAME=${APP_NAME:-"supermarket-app"}

# Build helper function
build_image() {
    local svc=$1
    echo "Building ${svc}..."
    docker build -t ${REGISTRY}/${APP_NAME}-${svc}:latest ./services/${svc}
    if [ "$PUSH" == "true" ]; then
        echo "Pushing ${svc} to ${REGISTRY}..."
        docker push ${REGISTRY}/${APP_NAME}-${svc}:latest
    fi
}

# Build each service
build_image bff-service
build_image core-service
build_image ui-service
build_image auth-service
build_image customer-mgmt

# If PUSH flag was provided and we didn't push during build (e.g. older script),
# ensure all images are pushed at least once.
if [ "$PUSH" == "true" ]; then
    echo "\nEnsuring all images are uploaded to ${REGISTRY}..."
    for svc in bff-service core-service ui-service auth-service customer-mgmt; do
        docker push ${REGISTRY}/${APP_NAME}-$svc:latest || true
    done
fi


# list created images
echo "\nImages created (tags start with ${REGISTRY}/${APP_NAME}-):"
docker images | grep "${APP_NAME}" || echo "No supermarket images found"

echo "All images built successfully!"
echo ""
echo "Images created:"
docker images | grep supermarket || echo "No supermarket images found"
