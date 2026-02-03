# Deployment Guide

Complete guide for deploying the Supermarket application to Kubernetes.

## Prerequisites

### Cluster Requirements
- Kubernetes 1.19+
- kubectl CLI tool
- Container runtime (Docker, containerd, etc.)
- Storage provisioner (for persistent volumes, optional)

### Local Development Requirements
- Docker 20.10+
- Docker Compose 1.29+
- At least 4GB free disk space
- At least 4GB free memory

## Option 1: Local Development with Docker Compose

### Step 1: Prerequisites

```bash
# Verify Docker is installed
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
cd /workspaces/Prometheus_Grafana-Learning/supermarket-app
```

### Step 3: Make Scripts Executable

```bash
chmod +x run-local.sh stop-local.sh
```

### Step 4: Start Services

```bash
./run-local.sh
```

The script will:
- Build Docker images
- Start all services
- Initialize volumes
- Wait for services to be ready

### Step 5: Verify Services

```bash
# Check running containers
docker-compose ps

# Test BFF service
curl http://localhost:5000/health

# Test Core service
curl http://localhost:5001/health

# Test UI service
curl http://localhost:5002/health
```

### Step 6: Access Services

| Service | URL |
|---------|-----|
| Web UI | http://localhost:5002 |
| BFF API | http://localhost:5000 |
| Core API | http://localhost:5001 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

### Step 7: Stop Services

```bash
./stop-local.sh
# Or: docker-compose down
```

## Option 2: Kubernetes Deployment

### Step 1: Prerequisites

```bash
# Verify kubectl is configured
kubectl cluster-info
kubectl get nodes

# Check cluster version
kubectl version
```

### Step 2: Build and Push Images

For local Kubernetes (minikube, kind, k3s):

```bash
# Make script executable
chmod +x build-images.sh

# Build images (will use local Docker daemon)
./build-images.sh

# Verify images
docker images | grep supermarket
```

For remote registry (Docker Hub, ECR, GCR, etc.):

```bash
# Build and tag with registry
docker build -t your-registry/supermarket/bff:latest ./services/bff
docker build -t your-registry/supermarket/core-service:latest ./services/core-service
docker build -t your-registry/supermarket/ui-service:latest ./services/ui-service

# Push to registry
docker push your-registry/supermarket/bff:latest
docker push your-registry/supermarket/core-service:latest
docker push your-registry/supermarket/ui-service:latest

# Update image references in k8s/services/*.yaml
sed -i 's|supermarket/|your-registry/supermarket/|g' k8s/services/*.yaml
```

### Step 3: Deploy to Kubernetes

```bash
# Make script executable
chmod +x deploy-k8s.sh

# Deploy
./deploy-k8s.sh
```

This will:
- Create namespaces
- Deploy services with replication
- Deploy monitoring stack
- Setup Kubernetes Dashboard
- Create RBAC rules

### Step 4: Verify Deployment

```bash
# Check namespaces
kubectl get namespaces

# Check supermarket services
kubectl get all -n supermarket

# Check monitoring
kubectl get all -n monitoring

# Check dashboard
kubectl get svc -n kubernetes-dashboard

# View pod status (wait for Running status)
kubectl get pods -n supermarket
kubectl get pods -n monitoring
```

### Step 5: Scale Services (Optional)

```bash
# Scale to 3 replicas
kubectl scale deployment bff-service -n supermarket --replicas=3
kubectl scale deployment core-service -n supermarket --replicas=3
kubectl scale deployment ui-service -n supermarket --replicas=3

# Verify scaling
kubectl get pods -n supermarket
```

### Step 6: Access Services

#### Port Forwarding

```bash
# BFF Service
kubectl port-forward -n supermarket svc/bff-service 5000:5000

# UI Service
kubectl port-forward -n supermarket svc/ui-service 5002:5002

# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Kubernetes Dashboard
kubectl port-forward -n kubernetes-dashboard svc/kubernetes-dashboard 8443:443
```

#### Using LoadBalancer

If your cluster supports LoadBalancer service type:

```bash
# Get external IPs
kubectl get svc -n supermarket
kubectl get svc -n monitoring

# Example output:
# NAME                TYPE           EXTERNAL-IP      PORT(S)
# bff-service         LoadBalancer   192.168.1.100    5000:30123/TCP
# ui-service          LoadBalancer   192.168.1.101    80:30456/TCP
# prometheus          LoadBalancer   192.168.1.102    9090:30789/TCP
# grafana             LoadBalancer   192.168.1.103    3000:30234/TCP

# Access services directly using EXTERNAL-IP
curl http://192.168.1.100:5000/health
```

## Common Deployment Scenarios

### Scenario 1: Development on minikube

```bash
# Start minikube
minikube start --memory=4096 --cpus=2

# Use Docker daemon inside minikube
eval $(minikube docker-env)

# Build images
chmod +x build-images.sh
./build-images.sh

# Deploy
chmod +x deploy-k8s.sh
./deploy-k8s.sh

# Access services
minikube service list -n supermarket

# Or use port forwarding
kubectl port-forward -n supermarket svc/ui-service 5002:5002
```

### Scenario 2: Development on kind (Kubernetes in Docker)

```bash
# Create cluster
kind create cluster --name supermarket

# Load images
docker build -t supermarket/bff:latest ./services/bff
kind load docker-image supermarket/bff:latest --name supermarket
kind load docker-image supermarket/core-service:latest --name supermarket
kind load docker-image supermarket/ui-service:latest --name supermarket

# Deploy
kubectl create -f k8s/monitoring/prometheus.yaml
kubectl create -f k8s/monitoring/grafana.yaml
kubectl create -f k8s/services/bff.yaml
kubectl create -f k8s/services/core-service.yaml
kubectl create -f k8s/services/ui-service.yaml

# Access via port-forward
kubectl port-forward -n supermarket svc/ui-service 5002:5002
```

### Scenario 3: Production on AWS EKS

```bash
# Configure AWS credentials
aws configure

# Create EKS cluster
eksctl create cluster \
  --name supermarket-prod \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name standard-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5

# Push images to ECR
aws ecr create-repository --repository-name supermarket/bff
aws ecr create-repository --repository-name supermarket/core-service
aws ecr create-repository --repository-name supermarket/ui-service

# Build and push images
docker build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/supermarket/bff:latest ./services/bff
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/supermarket/bff:latest
# Repeat for other services...

# Update image references in YAML files
sed -i 's|supermarket/|<account-id>.dkr.ecr.us-east-1.amazonaws.com/supermarket/|g' k8s/services/*.yaml

# Deploy
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/grafana.yaml
kubectl apply -f k8s/services/bff.yaml
kubectl apply -f k8s/services/core-service.yaml
kubectl apply -f k8s/services/ui-service.yaml

# Get LoadBalancer endpoints
kubectl get svc -n supermarket
```

### Scenario 4: Production on Google GKE

```bash
# Configure gcloud
gcloud config set project PROJECT_ID
gcloud auth login

# Create cluster
gcloud container clusters create supermarket-prod \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials supermarket-prod --zone us-central1-a

# Push images to GCR
docker build -t gcr.io/PROJECT_ID/supermarket/bff:latest ./services/bff
docker push gcr.io/PROJECT_ID/supermarket/bff:latest
# Repeat for other services...

# Update image references
sed -i 's|supermarket/|gcr.io/PROJECT_ID/supermarket/|g' k8s/services/*.yaml

# Deploy
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/grafana.yaml
kubectl apply -f k8s/services/bff.yaml
kubectl apply -f k8s/services/core-service.yaml
kubectl apply -f k8s/services/ui-service.yaml

# Get LoadBalancer endpoints
kubectl get svc -n supermarket
```

## Health Checks and Verification

### Check Deployment Status

```bash
# Detailed deployment status
kubectl describe deployment bff-service -n supermarket
kubectl describe deployment core-service -n supermarket
kubectl describe deployment ui-service -n supermarket

# Check for errors
kubectl get events -n supermarket
```

### Test Service Connectivity

```bash
# From within cluster (using a test pod)
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://bff-service:5000/health

# Check service discovery
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup bff-service.supermarket.svc.cluster.local
```

### Monitor Resource Usage

```bash
# View node resources
kubectl top nodes

# View pod resources
kubectl top pods -n supermarket
kubectl top pods -n monitoring

# Check persistent volumes (if using)
kubectl get pv
kubectl get pvc
```

## Updating Deployments

### Update Service Code

```bash
# Rebuild image
docker build -t supermarket/bff:v1.1 ./services/bff

# For local Kubernetes, load the image
kind load docker-image supermarket/bff:v1.1

# Update deployment with new image
kubectl set image deployment/bff-service \
  bff=supermarket/bff:v1.1 \
  -n supermarket

# Verify rollout
kubectl rollout status deployment/bff-service -n supermarket
```

### Rollback if Needed

```bash
# Check rollout history
kubectl rollout history deployment/bff-service -n supermarket

# Rollback to previous version
kubectl rollout undo deployment/bff-service -n supermarket
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap prometheus-config -n monitoring

# Restart Prometheus to apply changes
kubectl rollout restart deployment/prometheus -n monitoring
```

## Cleanup and Removal

### Remove Kubernetes Deployment

```bash
# Delete namespaces (removes all resources in namespace)
kubectl delete namespace supermarket
kubectl delete namespace monitoring
kubectl delete namespace kubernetes-dashboard

# Or delete specific resources
kubectl delete -f k8s/services/
kubectl delete -f k8s/monitoring/
```

### Remove Docker Compose Stack

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (persistent data)
docker-compose down -v

# Remove images
docker rmi supermarket/bff:latest
docker rmi supermarket/core-service:latest
docker rmi supermarket/ui-service:latest
```

## Troubleshooting Deployment

### Pods Not Starting

```bash
# Check pod logs
kubectl logs <pod-name> -n supermarket

# Describe pod for events
kubectl describe pod <pod-name> -n supermarket

# Check resource availability
kubectl top nodes
kubectl describe nodes
```

### Image Pull Errors

```bash
# Verify image exists
docker images | grep supermarket

# For local Kubernetes, load image
kind load docker-image supermarket/bff:latest

# Check image pull policy
kubectl get pod <pod-name> -n supermarket -o yaml | grep imagePullPolicy
```

### Service Connection Issues

```bash
# Check service endpoints
kubectl get endpoints -n supermarket

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup bff-service.supermarket.svc.cluster.local

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://bff-service:5000/health
```

### Storage Issues

```bash
# Check PersistentVolumes
kubectl get pv

# Check PersistentVolumeClaims
kubectl get pvc -n monitoring

# Describe PVC for issues
kubectl describe pvc <pvc-name> -n monitoring
```

## Performance Optimization

### Adjust Resource Requests/Limits

Edit `k8s/services/bff.yaml`:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

### Enable Horizontal Pod Autoscaling

```bash
# Create autoscaling policy
kubectl autoscale deployment bff-service \
  -n supermarket \
  --min=2 \
  --max=5 \
  --cpu-percent=80

# Check HPA status
kubectl get hpa -n supermarket
```

### Use Node Selectors for Placement

Add to deployment spec:

```yaml
spec:
  nodeSelector:
    workload: compute  # Label your nodes accordingly
```

## Backup and Disaster Recovery

### Backup Application Configuration

```bash
# Backup all Kubernetes resources
kubectl get all -n supermarket -o yaml > supermarket-backup.yaml
kubectl get all -n monitoring -o yaml > monitoring-backup.yaml

# Backup ConfigMaps and Secrets
kubectl get configmap,secret -n monitoring -o yaml > monitoring-configs.yaml
```

### Restore from Backup

```bash
kubectl apply -f supermarket-backup.yaml
kubectl apply -f monitoring-configs.yaml
```

## Next Steps

1. Configure ingress for external access
2. Set up persistent volumes for data
3. Enable TLS/HTTPS
4. Configure RBAC policies
5. Implement backup strategies
6. Set up CI/CD pipeline
7. Configure autoscaling
8. Implement network policies
