"""
BFF (Backend for Frontend) Service
Handles client requests and coordinates with core services
"""
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import requests
from datetime import datetime

app = Flask(__name__)

# Prometheus metrics
request_count = Counter('bff_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('bff_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
core_service_calls = Counter('bff_core_service_calls_total', 'Core service calls', ['endpoint'])

# Configuration
CORE_SERVICE_URL = "http://core-service:5001"

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        request_duration.labels(method=request.method, endpoint=request.path).observe(duration)
    request_count.labels(method=request.method, endpoint=request.path).inc()
    return response

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'bff', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    """Get all products or create new product"""
    try:
        core_service_calls.labels(endpoint='products').inc()
        if request.method == 'POST':
            response = requests.post(f"{CORE_SERVICE_URL}/products", json=request.get_json(), timeout=5)
        else:
            response = requests.get(f"{CORE_SERVICE_URL}/products", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get inventory information"""
    try:
        core_service_calls.labels(endpoint='inventory').inc()
        response = requests.get(f"{CORE_SERVICE_URL}/inventory", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    try:
        core_service_calls.labels(endpoint='product_detail').inc()
        response = requests.get(f"{CORE_SERVICE_URL}/products/{product_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        core_service_calls.labels(endpoint='orders').inc()
        data = request.get_json()
        response = requests.post(f"{CORE_SERVICE_URL}/orders", json=data, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        core_service_calls.labels(endpoint='order_detail').inc()
        response = requests.get(f"{CORE_SERVICE_URL}/orders/{order_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
