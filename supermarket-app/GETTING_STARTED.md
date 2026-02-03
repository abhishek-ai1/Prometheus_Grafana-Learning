# Getting Started - 5 Minutes

The fastest way to get the Supermarket application up and running.

## Prerequisites

- Docker & Docker Compose installed
- OR: kubectl configured with access to a Kubernetes cluster

## Option 1: Local Docker Compose (2 Minutes)

### Step 1: Navigate to Project

```bash
cd /workspaces/Prometheus_Grafana-Learning/supermarket-app
```

### Step 2: Start Stack

```bash
chmod +x run-local.sh
./run-local.sh
```

Wait 10-15 seconds for services to start...

### Step 3: Access Services

Open in browser or use curl:

```bash
# Web UI
http://localhost:5002

# Grafana Dashboard
http://localhost:3000
# Login: admin / admin

# Prometheus
http://localhost:9090

# API Testing
curl http://localhost:5000/api/products
```

### Step 4: Test an API Call

```bash
# Create an order
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "name": "Milk", "price": 3.99, "quantity": 1}
    ]
  }'
```

### Step 5: View Metrics

```bash
# Open Prometheus
http://localhost:9090

# Try this query
rate(bff_requests_total[5m])
```

### Stop Services

```bash
chmod +x stop-local.sh
./stop-local.sh
```

---

## Option 2: Kubernetes (5-10 Minutes)

### Step 1: Build Images

```bash
cd /workspaces/Prometheus_Grafana-Learning/supermarket-app
chmod +x build-images.sh
./build-images.sh
```

### Step 2: Deploy

```bash
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

### Step 3: Verify Deployment

```bash
kubectl get pods -n supermarket
kubectl get pods -n monitoring
```

Wait until all pods are `Running`...

### Step 4: Access Services

```bash
# Terminal 1: Port-forward to UI
kubectl port-forward -n supermarket svc/ui-service 5002:5002

# Terminal 2: Port-forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Terminal 3: Port-forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

### Step 5: Open in Browser

- UI: http://localhost:5002
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

---

## Quick Test Checklist

- [ ] UI loads (http://localhost:5002)
- [ ] Can browse products
- [ ] Can create orders via API
- [ ] Grafana accessible (admin/admin)
- [ ] Prometheus collecting metrics
- [ ] Dashboard shows real-time metrics

---

## Common Commands

```bash
# View logs
docker-compose logs -f bff-service

# Check service health
curl http://localhost:5000/health

# Get all products
curl http://localhost:5000/api/products

# Get metrics
curl http://localhost:5000/metrics

# Scale services (Kubernetes)
kubectl scale deployment bff-service --replicas=5 -n supermarket

# View resource usage
kubectl top pods -n supermarket
```

---

## Next Steps

1. Read [README.md](README.md) for complete overview
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more commands
3. Explore [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details

---

## Troubleshooting

### Docker Compose won't start

```bash
# Check Docker is running
docker ps

# Check for port conflicts
docker ps -a

# Rebuild from scratch
docker-compose down -v
./run-local.sh
```

### Kubernetes pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n supermarket

# View logs
kubectl logs <pod-name> -n supermarket

# Verify images exist
docker images | grep supermarket
```

### Can't access services

```bash
# Verify services are running
docker-compose ps
# or
kubectl get svc -n supermarket

# Check port forwarding
netstat -tln | grep 5000
```

---

**That's it! You're ready to explore the Supermarket microservices application!**
