# 🚀 Quick Start Guide - Professional UI & Monitoring

## 🎯 What's Ready

Your Supermarket app now has:
- ✅ Professional modern UI across all pages
- ✅ Real-time system monitoring dashboard
- ✅ Prometheus & Grafana integration
- ✅ Service health visibility
- ✅ Real-time metrics and charts

## 📍 Access Points

### Main Application
```
🏠 Home:           http://localhost:5002
🛍️ Products:        http://localhost:5002/products
🛒 Cart:            http://localhost:5002/cart
📋 Orders:          http://localhost:5002/orders
📊 Inventory:       http://localhost:5002/inventory
⚙️ Admin:           http://localhost:5002/admin
```

### ⭐ NEW Monitoring
```
📈 System Status:   http://localhost:5002/monitoring
```

### External Tools
```
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3000
```

## 🎨 Design Features

### Home Page Features
```
✨ Gradient animated header
🎯 Hero section with CTAs
📊 Feature showcase cards
📈 System statistics display
🎭 Smooth animations
📱 Fully responsive
```

### Products Page Features
```
🔍 Search functionality
🏷️ Category filtering
💰 Price range filters
📦 Professional card layout
🖼️ Emoji product icons
➕ Add to cart (quantity increment)
📱 Responsive grid
```

### Monitoring Dashboard Features
```
❤️ Service health status (5 services)
📊 Request rate chart
⏱️ Response time visualization
📈 System statistics (4 key metrics)
🔗 API endpoints reference
🔄 Auto-refresh every 30 seconds
📱 Professional, responsive layout
```

## 🏃 Quick Commands

### View Logs
```bash
# UI Service logs
docker-compose logs -f ui-service

# BFF Service logs
docker-compose logs -f bff-service

# Core Service logs
docker-compose logs -f core-service

# Prometheus logs
docker-compose logs -f prometheus

# Grafana logs
docker-compose logs -f grafana
```

### Check Service Status
```bash
# All services
docker-compose ps

# Health check
curl http://localhost:5002/health
curl http://localhost:5000/health
curl http://localhost:5001/health
```

### View Metrics
```bash
# UI Service metrics
curl http://localhost:5002/metrics

# BFF Service metrics
curl http://localhost:5000/metrics

# Core Service metrics
curl http://localhost:5001/metrics
```

### Test API Endpoints
```bash
# Get products
curl http://localhost:5000/api/products | json_pp

# Get inventory
curl http://localhost:5000/api/inventory | json_pp

# Get orders
curl http://localhost:5000/api/orders | json_pp
```

## 📊 Monitoring Dashboard Guide

### What You See

**Service Cards (Top Section)**
- Shows all 5 services: BFF, Core, UI, Prometheus, Grafana
- Each card displays:
  - Service name
  - Status (✅ Healthy or ❌ Unhealthy)
  - Port number
  - Current status (Running/Offline)
  - Service URL

**Statistics (Middle Section)**
- **Total Requests**: How many API calls have been made
- **Average Response Time**: Typical latency in milliseconds
- **Services Up**: Count of healthy services (e.g., 5/5)
- **Active Connections**: Current active client connections

**Charts (Charts Section)**
1. **Request Rate Chart (Line Graph)**
   - Shows BFF and Core Service requests over time
   - Time range: Last 10 minutes
   - Updates with auto-refresh

2. **Response Time Distribution (Doughnut Chart)**
   - 🟢 0-50ms: Green (fast)
   - 🟡 50-100ms: Yellow (acceptable)
   - 🟠 100-200ms: Orange (slow)
   - 🔴 200ms+: Red (very slow)

**API Endpoints List (Bottom Section)**
- Lists all available endpoints
- Shows HTTP method (GET/POST) with color coding
- Organized by service
- Real-time availability status

### How to Use

1. **Check System Health**
   - Open `/monitoring`
   - Look for ✅ status badges (all should be green)
   - If any shows ❌, investigate that service

2. **Monitor Performance**
   - View the "Request Rate" chart
   - Higher lines = more traffic
   - Watch for sudden spikes or drops

3. **Analyze Response Times**
   - Check the "Response Time Distribution" chart
   - Most responses should be in the 0-50ms range
   - If many are slow (100ms+), investigate performance

4. **View Statistics**
   - Monitor "Total Requests" to see traffic volume
   - Track "Services Up" to ensure all services are running
   - Watch "Active Connections" for connection health

5. **Refresh for Latest Data**
   - Dashboard auto-refreshes every 30 seconds
   - Click "Refresh" button for immediate update

## 🛍️ Shopping Experience

### Browse Products
1. Go to `/products`
2. Use filters on the left:
   - Select categories (with emoji icons)
   - Choose price range
3. Search for specific items
4. Click "Add to Cart" to purchase

### Manage Cart
1. Go to `/cart`
2. Adjust quantities with +/- buttons
3. View order summary
4. Click "Place Order"

### View Orders
1. Go to `/orders`
2. Filter by status (Placed, Processing, Delivered)
3. See order details and items

### Admin Panel
1. Go to `/admin`
2. Add new products
3. Manage inventory levels
4. View statistics

## 🔧 Troubleshooting

### Service Not Responding
```bash
# Check if service is running
docker-compose ps

# If not, restart it
docker-compose restart ui-service

# Check logs
docker-compose logs ui-service
```

### Monitoring Dashboard Shows ❌
```bash
# Check service health
curl http://localhost:5002/health

# Restart if needed
docker-compose restart ui-service

# Check logs
docker-compose logs ui-service
```

### Prometheus Not Collecting Metrics
```bash
# Verify Prometheus is running
curl http://localhost:9090

# Check Prometheus targets
http://localhost:9090/targets

# Verify services have metrics endpoint
curl http://localhost:5002/metrics
```

### Grafana Shows No Data
```bash
# Check if Prometheus datasource is configured
# Go to http://localhost:3000/datasources
# Click on Prometheus
# Click "Save & Test"

# Verify data in Prometheus
# Go to http://localhost:9090
# Try a simple query: up
```

## 📈 Key Metrics to Watch

| Metric | What It Means | Healthy Range |
|--------|---------------|---------------|
| Request Rate | API calls per minute | Varies by usage |
| Response Time (P95) | 95th percentile latency | < 100ms |
| Error Rate | Failed requests % | < 1% |
| Services Up | Count of healthy services | 5/5 |
| Active Connections | Current users | Varies |

## 🎯 Common Tasks

### Add a New Product
1. Go to `/admin`
2. Fill in product details
3. Select category
4. Click "Add Product"

### Check Inventory
1. Go to `/inventory`
2. View current stock levels
3. Identify low-stock items

### Monitor System Health
1. Go to `/monitoring`
2. Check service status cards
3. Review metrics charts
4. Look for any red/warning indicators

### Export Metrics
1. Go to Prometheus (`http://localhost:9090`)
2. Run a query
3. Use "Export" option

## 📚 Documentation Files

- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Full feature list
- **[UI_ENHANCEMENTS.md](UI_ENHANCEMENTS.md)** - Detailed UI changes
- **[PROMETHEUS_GRAFANA.md](PROMETHEUS_GRAFANA.md)** - Monitoring setup
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

## 🎓 Learning Resources

### Understanding the Monitoring Stack
1. Start with home page (`/`) - See feature overview
2. Visit `/monitoring` - See live metrics
3. Explore Prometheus (`http://localhost:9090`) - Advanced queries
4. Create dashboards in Grafana (`http://localhost:3000`)

### Key Concepts

**Health Checks**: Each service responds to `/health` to confirm it's running

**Metrics**: Each service exposes `/metrics` in Prometheus format

**Prometheus**: Collects metrics from all services and stores them

**Grafana**: Creates dashboards from Prometheus data

**Monitoring Dashboard**: Custom in-app view of system health

## 🚀 Next Steps

1. ✅ Explore all pages - See the new design
2. ✅ Check `/monitoring` - View system status
3. ✅ Add products in `/admin` - Populate inventory
4. ✅ Shop in `/products` - Browse with filters
5. ✅ View `/orders` - See order history
6. ✅ Monitor in Prometheus - Run custom queries
7. ✅ Build dashboards in Grafana - Create visualizations

## 💬 Support

If you encounter issues:
1. Check service status: `docker-compose ps`
2. Review logs: `docker-compose logs -f service-name`
3. Verify connectivity: `curl http://localhost:port/health`
4. Check documentation files for detailed guides

---

**Ready to explore?** Start with `http://localhost:5002/` and then check `http://localhost:5002/monitoring` for system status! 🎉
