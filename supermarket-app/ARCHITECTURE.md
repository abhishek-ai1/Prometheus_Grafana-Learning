# Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SUPERMARKET APPLICATION                      │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    KUBERNETES CLUSTER                         │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │          SUPERMARKET NAMESPACE                          │ │  │
│  │  │                                                          │ │  │
│  │  │  ┌──────────────┐  ┌─────────────────────────────────┐ │ │  │
│  │  │  │  UI Service  │  │                                 │ │ │  │
│  │  │  │   (5002)     │  │  ┌──────────────────────────┐   │ │ │  │
│  │  │  │ Replicas: 2  │  │  │    BFF Service (5000)    │   │ │ │  │
│  │  │  └──────┬───────┘  │  │   Replicas: 2            │   │ │ │  │
│  │  │         │          │  │  ┌────────────────────┐  │   │ │ │  │
│  │  │  ┌──────▼────────────────►  Core Service     │  │   │ │ │  │
│  │  │  │  LoadBalancer  │  │  │   (5001)          │  │   │ │ │  │
│  │  │  │  (Port 5002)   │  │  │   Replicas: 2    │  │   │ │ │  │
│  │  │  └────────────────┘  │  └────────────────────┘  │   │ │ │  │
│  │  │                      └─────────────────────────────┘ │ │  │
│  │  │                                                      │ │  │
│  │  │  Health Checks & Prometheus Metrics                 │ │  │
│  │  │  GET /health                                        │ │  │
│  │  │  GET /metrics                                       │ │  │
│  │  │                                                      │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │          MONITORING NAMESPACE                       │  │  │
│  │  │                                                     │  │  │
│  │  │  ┌──────────────────────────────────────────────┐ │  │  │
│  │  │  │  Prometheus (Port 9090)                      │ │  │  │
│  │  │  │  - Scrapes metrics every 15s                 │ │  │  │
│  │  │  │  - Stores for 30 days                        │ │  │  │
│  │  │  │  - Auto-discovers via K8s API               │ │  │  │
│  │  │  │  - 1 replica                                 │ │  │  │
│  │  │  └──────────────────────────────────────────────┘ │  │  │
│  │  │                                                     │  │  │
│  │  │  ┌──────────────────────────────────────────────┐ │  │  │
│  │  │  │  Grafana (Port 3000)                         │ │  │  │
│  │  │  │  - Dashboard visualization                   │ │  │  │
│  │  │  │  - Pre-configured Prometheus datasource      │ │  │  │
│  │  │  │  - Admin/Admin credentials                   │ │  │  │
│  │  │  │  - 1 replica                                 │ │  │  │
│  │  │  └──────────────────────────────────────────────┘ │  │  │
│  │  │                                                     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │          KUBERNETES DASHBOARD NAMESPACE             │  │  │
│  │  │  - Cluster management UI                            │  │  │
│  │  │  - Pod and service monitoring                       │  │  │
│  │  │  - Admin user with cluster-admin role              │  │  │
│  │  │  - Port 8443 (HTTPS)                                │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
CLIENT
  │
  ├─► UI Service (5002) ──► Products/Orders HTML
  │      │
  │      ├─► Metrics (/metrics)
  │      │      │
  │      │      ▼
  │      └──► Prometheus (9090) ──► Stores Time-Series Data
  │                                    │
  │                                    ▼
  │                                 Grafana (3000)
  │                                 (Dashboard)
  │
  ├─► BFF Service (5000)
  │      │
  │      ├─► REST API Gateway
  │      │      │
  │      │      ├─ GET  /api/products
  │      │      ├─ GET  /api/products/{id}
  │      │      ├─ POST /api/orders
  │      │      └─ GET  /api/orders/{id}
  │      │
  │      ├─► Metrics (/metrics)
  │      │
  │      └──► Core Service (5001)
  │             │
  │             ├─► Business Logic
  │             ├─► Product Management
  │             ├─► Order Processing
  │             ├─► Inventory Management
  │             │
  │             └─► Metrics (/metrics)
  │
  └─► Prometheus
       │
       ├─ Scrapes:
       │  ├─ BFF /metrics
       │  ├─ Core /metrics
       │  ├─ UI /metrics
       │  ├─ K8s API Server
       │  ├─ Node exporters
       │  └─ Pod metrics
       │
       └─ Time-Series Storage
          ├─ Requests/sec
          ├─ Latency (ms)
          ├─ Error rates
          ├─ Orders created
          └─ Products queried
```

## Service Communication

```
┌─────────────────────────────────────┐
│     CLIENT APPLICATION              │
│     (Browser / API Client)          │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐    ┌──────────────┐
│  UI Service  │    │  BFF Service │
│   (5002)     │    │   (5000)     │
└──────────────┘    └──────┬───────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Core Service    │
                  │   (5001)         │
                  └──────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         ┌────────────────┐   ┌────────────────┐
         │ Products Data  │   │  Orders Data   │
         │  (In Memory)   │   │  (In Memory)   │
         └────────────────┘   └────────────────┘
```

## Monitoring Flow

```
┌──────────────────────────────────────────┐
│         MICROSERVICES                    │
│  (BFF, Core Service, UI)                 │
│  - Collect Prometheus metrics            │
│  - Expose on /metrics endpoint           │
│  - Include annotations for K8s discovery │
└────────────────┬─────────────────────────┘
                 │
                 │ HTTP GET /metrics
                 │ (every 15 seconds)
                 │
                 ▼
┌──────────────────────────────────────────┐
│         PROMETHEUS (9090)                │
│  ┌──────────────────────────────────────┐│
│  │ Service Discovery                    ││
│  │ - Queries K8s API                    ││
│  │ - Finds pods with prometheus.io      ││
│  │   annotations                        ││
│  │ - Auto-discovers metric endpoints    ││
│  └──────────────────────────────────────┘│
│  ┌──────────────────────────────────────┐│
│  │ Time-Series Database (TSDB)          ││
│  │ - Stores metrics                     ││
│  │ - Retention: 30 days                 ││
│  │ - Indexed for fast queries           ││
│  └──────────────────────────────────────┘│
└────────────────┬─────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    PromQL               HTTP
    Queries              API
         │                │
         ▼                ▼
┌──────────────────────────────────────────┐
│         GRAFANA (3000)                   │
│  ┌──────────────────────────────────────┐│
│  │ Dashboards                           ││
│  │ - Visualize metrics                  ││
│  │ - Custom queries                     ││
│  │ - Real-time updates                  ││
│  │ - Alerting                           ││
│  └──────────────────────────────────────┘│
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│      VISUALIZATION & ANALYSIS            │
│  - System performance                    │
│  - Error rates                           │
│  - Business metrics                      │
│  - Resource usage                        │
└──────────────────────────────────────────┘
```

## Deployment Architecture

```
LOCAL DEVELOPMENT                  KUBERNETES PRODUCTION
─────────────────────             ──────────────────────

Docker Host                        Kubernetes Cluster
  │                                  │
  ├─ bff-service:5000                ├─ Node 1
  │                                  │  ├─ BFF Pod
  ├─ core-service:5001               │  └─ Core Service Pod
  │                                  │
  ├─ ui-service:5002                 ├─ Node 2
  │                                  │  ├─ UI Service Pod
  ├─ prometheus:9090                 │  └─ Core Service Pod
  │                                  │
  ├─ grafana:3000                    ├─ Node 3
  │                                  │  ├─ Prometheus
  └─ volumes                         │  └─ Grafana
     ├─ prometheus-storage           │
     └─ grafana-storage              ├─ Service Discovery
                                     │  └─ K8s API Server
                                     │
                                     ├─ ConfigMaps
                                     │  └─ Prometheus Config
                                     │
                                     ├─ ServiceAccounts
                                     │  └─ RBAC Roles
                                     │
                                     └─ PersistentVolumes
                                        (Optional)
```

## Kubernetes Resources

```
┌─────────────────────────────────────────────────┐
│            KUBERNETES RESOURCES                  │
│                                                 │
│ NAMESPACES                                      │
│  ├─ supermarket                                 │
│  ├─ monitoring                                  │
│  └─ kubernetes-dashboard                        │
│                                                 │
│ DEPLOYMENTS (Per Service)                       │
│  ├─ bff-service                                 │
│  │  └─ replicas: 2                              │
│  ├─ core-service                                │
│  │  └─ replicas: 2                              │
│  ├─ ui-service                                  │
│  │  └─ replicas: 2                              │
│  ├─ prometheus                                  │
│  │  └─ replicas: 1                              │
│  └─ grafana                                     │
│     └─ replicas: 1                              │
│                                                 │
│ SERVICES (Per Deployment)                       │
│  ├─ bff-service: LoadBalancer (5000:5000)      │
│  ├─ core-service: ClusterIP (5001:5001)        │
│  ├─ ui-service: LoadBalancer (80:5002)         │
│  ├─ prometheus: LoadBalancer (9090:9090)       │
│  └─ grafana: LoadBalancer (3000:3000)          │
│                                                 │
│ CONFIGMAPS                                      │
│  └─ prometheus-config                           │
│     └─ grafana-datasources                      │
│     └─ grafana-dashboard-provider               │
│     └─ grafana-dashboards                       │
│                                                 │
│ SERVICEACCOUNTS                                 │
│  ├─ prometheus (for K8s discovery)              │
│  └─ admin-user (for dashboard)                  │
│                                                 │
│ ROLES & ROLEBINDINGS                            │
│  ├─ prometheus ClusterRole                      │
│  ├─ prometheus ClusterRoleBinding               │
│  └─ admin-user ClusterRoleBinding               │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Request Flow Example

### API Request Flow

```
1. USER/CLIENT
   │
   ├─ HTTP GET /api/products
   │
   ▼
2. LOAD BALANCER
   └─ Routes to BFF Service instance
   │
   ▼
3. BFF SERVICE
   │
   ├─ Records metric: bff_requests_total++
   ├─ Starts timer for request duration
   │
   ▼
4. BFF calls Core Service
   │
   ├─ Records metric: bff_core_service_calls_total++
   │
   ▼
5. CORE SERVICE
   │
   ├─ Records metric: core_service_requests_total++
   ├─ Starts timer
   ├─ Queries product database
   │
   ▼
6. RESPONSE SENT
   │
   ├─ Stop timer: bff_request_duration_seconds
   ├─ Stop timer: core_service_request_duration_seconds
   ├─ Records metrics in Prometheus
   │
   ▼
7. PROMETHEUS SCRAPES (every 15s)
   │
   ├─ GET /metrics from BFF
   ├─ GET /metrics from Core
   ├─ Stores time-series data
   │
   ▼
8. GRAFANA QUERIES (user dashboard)
   │
   ├─ PromQL: rate(bff_requests_total[5m])
   ├─ Displays on dashboard
   │
   ▼
9. VISUALIZATION
   │
   ├─ Real-time metrics graph
   ├─ Request rate, latency, errors
   └─ Performance analysis
```

## Scaling Architecture

```
┌──────────────────────────────────────────────────┐
│        HORIZONTAL SCALING (MORE REPLICAS)        │
│                                                  │
│ Initial State (replicas: 2)                      │
│ ┌──────────────────┐  ┌──────────────────┐     │
│ │  BFF Pod 1       │  │  BFF Pod 2       │     │
│ │  (5000)          │  │  (5000)          │     │
│ └────────┬─────────┘  └────────┬─────────┘     │
│          │                     │                │
│          └─────────┬───────────┘                │
│                    ▼                            │
│          BFF Service (LoadBalancer)             │
│          Round-robin distribution              │
│                                                 │
│ After Scaling (replicas: 5)                     │
│ ┌────────────────────────────────────────┐    │
│ │  BFF Pod 1   │  Pod 2   │  Pod 3       │    │
│ │  Pod 4       │  Pod 5   │              │    │
│ └────────────────────────────────────────┘    │
│          │                                     │
│          ▼                                     │
│  BFF Service (LoadBalancer)                    │
│  - Better throughput                           │
│  - Better fault tolerance                      │
│  - Reduced latency per instance                │
│                                                 │
└──────────────────────────────────────────────────┘
```

## Persistence Strategy (Optional)

```
┌─────────────────────────────────────────┐
│     PERSISTENT VOLUME SETUP             │
│                                         │
│ Prometheus Data                         │
│ ┌─────────────────────────────────────┐│
│ │ PV: prometheus-storage-pv            ││
│ │ PVC: prometheus-storage-pvc          ││
│ │ Size: 50Gi (configurable)            ││
│ │ Type: local/network storage          ││
│ └─────────────────────────────────────┘│
│           ▲                             │
│           │                             │
│           │ Mount at /prometheus       │
│           │                             │
│ ┌─────────┴─────────────────────────┐  │
│ │   Prometheus StatefulSet          │  │
│ │   (with persistent volume)        │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Grafana Data                            │
│ ┌─────────────────────────────────────┐│
│ │ PV: grafana-storage-pv               ││
│ │ PVC: grafana-storage-pvc             ││
│ │ Size: 10Gi (configurable)            ││
│ │ Type: local/network storage          ││
│ └─────────────────────────────────────┘│
│           ▲                             │
│           │                             │
│           │ Mount at /var/lib/grafana  │
│           │                             │
│ ┌─────────┴─────────────────────────┐  │
│ │   Grafana StatefulSet             │  │
│ │   (with persistent volume)        │  │
│ └───────────────────────────────────┘  │
│                                         │
│ Retention Policies:                     │
│ - Prometheus: 30 days                   │
│ - Grafana: Indefinite                   │
│                                         │
└─────────────────────────────────────────┘
```
