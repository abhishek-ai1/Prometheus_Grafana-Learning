#!/bin/bash

# Deploy to Kubernetes
# This script deploys the supermarket application and monitoring stack to Kubernetes

set -e

echo "Starting Kubernetes deployment..."

# Create monitoring namespace
echo "Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Deploy Prometheus
echo "Deploying Prometheus..."
kubectl apply -f k8s/monitoring/prometheus.yaml

# Deploy Grafana
echo "Deploying Grafana..."
kubectl apply -f k8s/monitoring/grafana.yaml

# Deploy BFF Service
echo "Deploying BFF Service..."
kubectl apply -f k8s/services/bff.yaml

# Deploy Core Service
echo "Deploying Core Service..."
kubectl apply -f k8s/services/core-service.yaml

# Deploy UI Service
echo "Deploying UI Service..."
kubectl apply -f k8s/services/ui-service.yaml

# Deploy Kubernetes Dashboard
echo "Deploying Kubernetes Dashboard..."
kubectl apply -f k8s/dashboard/dashboard-user.yaml

echo ""
echo "Deployment complete!"
echo ""
echo "Checking service status..."
kubectl get ns
echo ""
echo "Supermarket Services:"
kubectl get pods,svc -n supermarket
echo ""
echo "Monitoring Stack:"
kubectl get pods,svc -n monitoring
echo ""
echo "Dashboard:"
kubectl get svc -n kubernetes-dashboard
