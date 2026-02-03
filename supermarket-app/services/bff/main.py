"""
BFF (Backend for Frontend) Service
Handles client requests and coordinates with core services
"""
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Prometheus metrics
request_count = Counter('bff_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('bff_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
core_service_calls = Counter('bff_core_service_calls_total', 'Core service calls', ['endpoint'])
auth_service_calls = Counter('bff_auth_service_calls_total', 'Auth service calls', ['endpoint'])
customer_mgmt_calls = Counter('bff_customer_mgmt_calls_total', 'Customer mgmt calls', ['endpoint'])

# Configuration
CORE_SERVICE_URL = os.getenv('CORE_SERVICE_URL', 'http://core-service:5001')
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5003')
CUSTOMER_MGMT_URL = os.getenv('CUSTOMER_MGMT_URL', 'http://customer-mgmt:5004')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        request_duration.labels(method=request.method, endpoint=request.path).observe(duration)
    request_count.labels(method=request.method, endpoint=request.path).inc()
    # CORS: respect ALLOWED_ORIGINS env var (defaults to '*')
    allowed = os.getenv('ALLOWED_ORIGINS', '*')
    response.headers['Access-Control-Allow-Origin'] = allowed
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'bff', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# ==================== Auth Service Proxies ====================

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Proxy login request to auth service"""
    try:
        auth_service_calls.labels(endpoint='login').inc()
        response = requests.post(f"{AUTH_SERVICE_URL}/api/auth/login", json=request.get_json(), timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/auth/verify', methods=['GET'])
def auth_verify():
    """Proxy token verification to auth service"""
    try:
        auth_service_calls.labels(endpoint='verify').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/verify", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/auth/permissions', methods=['GET'])
def auth_permissions():
    """Proxy permissions request to auth service"""
    try:
        auth_service_calls.labels(endpoint='permissions').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/permissions", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/auth/refresh', methods=['POST'])
def auth_refresh():
    """Proxy token refresh to auth service"""
    try:
        auth_service_calls.labels(endpoint='refresh').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.post(f"{AUTH_SERVICE_URL}/api/auth/refresh", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Proxy logout to auth service"""
    try:
        auth_service_calls.labels(endpoint='logout').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.post(f"{AUTH_SERVICE_URL}/api/auth/logout", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== User Management (Admin) ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    try:
        auth_service_calls.labels(endpoint='get_users').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/users", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user (admin only)"""
    try:
        auth_service_calls.labels(endpoint='create_user').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.post(f"{AUTH_SERVICE_URL}/api/users", json=request.get_json(), headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user (admin only)"""
    try:
        auth_service_calls.labels(endpoint='update_user').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.put(f"{AUTH_SERVICE_URL}/api/users/{user_id}", json=request.get_json(), headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        auth_service_calls.labels(endpoint='delete_user').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.delete(f"{AUTH_SERVICE_URL}/api/users/{user_id}", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/roles', methods=['GET'])
def get_roles():
    """Get all roles (admin only)"""
    try:
        auth_service_calls.labels(endpoint='get_roles').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/roles", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/api/audit', methods=['GET'])
def proxy_audit():
    """Proxy audit log access to auth service (admin only at auth)"""
    try:
        auth_service_calls.labels(endpoint='audit').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/audit", headers=headers, params=request.args, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== Customer Management Proxies ====================

@app.route('/api/customers/me', methods=['GET', 'PUT'])
def manage_customer_profile():
    """Proxy customer profile requests"""
    try:
        customer_mgmt_calls.labels(endpoint='profile').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        
        if request.method == 'GET':
            response = requests.get(f"{CUSTOMER_MGMT_URL}/api/customers/me", headers=headers, timeout=5)
        else:
            response = requests.put(f"{CUSTOMER_MGMT_URL}/api/customers/me", json=request.get_json(), headers=headers, timeout=5)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer profile by ID"""
    try:
        customer_mgmt_calls.labels(endpoint='customer_detail').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{CUSTOMER_MGMT_URL}/api/customers/{customer_id}", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/customers', methods=['GET'])
def list_customers():
    """List all customers"""
    try:
        customer_mgmt_calls.labels(endpoint='list_customers').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{CUSTOMER_MGMT_URL}/api/customers", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/customers/me/orders', methods=['GET'])
def get_customer_orders():
    """Get customer orders"""
    try:
        customer_mgmt_calls.labels(endpoint='customer_orders').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{CUSTOMER_MGMT_URL}/api/customers/me/orders", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/customers/me/loyalty', methods=['GET'])
def get_loyalty_info():
    """Get customer loyalty info"""
    try:
        customer_mgmt_calls.labels(endpoint='loyalty').inc()
        headers = {'Authorization': request.headers.get('Authorization', '')}
        response = requests.get(f"{CUSTOMER_MGMT_URL}/api/customers/me/loyalty", headers=headers, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

# ==================== Core Service Proxies ====================

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
