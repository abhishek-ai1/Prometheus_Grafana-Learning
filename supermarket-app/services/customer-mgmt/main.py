"""
Customer Management Service
Handles customer profiles, preferences, and related operations
"""
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import time
import os
from functools import wraps
import requests

app = Flask(__name__)

# Prometheus metrics
request_count = Counter('customer_mgmt_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('customer_mgmt_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
customer_operations = Counter('customer_operations_total', 'Customer operations', ['operation'])

# Configuration
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5003')

# In-memory customer database
customers_db = {
    '1': {
        'id': '1',
        'email': 'customer@supermarket.com',
        'name': 'Customer User',
        'phone': '555-0001',
        'address': '123 Main St',
        'city': 'Anytown',
        'state': 'ST',
        'zip': '12345',
        'country': 'USA',
        'membership_level': 'silver',
        'total_orders': 5,
        'total_spent': 250.00,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
}

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

def verify_token(token):
    """Verify token with auth service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{AUTH_SERVICE_URL}/api/auth/verify', headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def token_required(f):
    """Decorator to check JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        auth_data = verify_token(token)
        if not auth_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = auth_data.get('user', {})
        return f(*args, **kwargs)
    
    return decorated

# ==================== Health & Metrics ====================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'customer-mgmt', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# ==================== Customer Profile ====================

@app.route('/api/customers/me', methods=['GET'])
@token_required
def get_current_customer():
    """Get current logged-in customer profile"""
    user_email = request.user.get('email')
    
    # Find customer by email
    for customer_id, customer in customers_db.items():
        if customer['email'] == user_email:
            customer_operations.labels(operation='profile_view').inc()
            return jsonify(customer), 200
    
    # Return minimal profile if customer not found
    return jsonify({
        'email': user_email,
        'name': request.user.get('name'),
        'message': 'Customer profile not yet created'
    }), 200

@app.route('/api/customers/me', methods=['PUT'])
@token_required
def update_current_customer():
    """Update current customer profile"""
    data = request.get_json()
    user_email = request.user.get('email')
    
    customer_id = None
    for cid, customer in customers_db.items():
        if customer['email'] == user_email:
            customer_id = cid
            break
    
    if not customer_id:
        # Create new customer profile
        customer_id = str(len(customers_db) + 1)
        customers_db[customer_id] = {
            'id': customer_id,
            'email': user_email,
            'name': request.user.get('name', 'Customer'),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'zip': data.get('zip', ''),
            'country': data.get('country', 'USA'),
            'membership_level': 'bronze',
            'total_orders': 0,
            'total_spent': 0.0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    else:
        customer = customers_db[customer_id]
        if 'name' in data:
            customer['name'] = data['name']
        if 'phone' in data:
            customer['phone'] = data['phone']
        if 'address' in data:
            customer['address'] = data['address']
        if 'city' in data:
            customer['city'] = data['city']
        if 'state' in data:
            customer['state'] = data['state']
        if 'zip' in data:
            customer['zip'] = data['zip']
        if 'country' in data:
            customer['country'] = data['country']
        customer['updated_at'] = datetime.now().isoformat()
    
    customer_operations.labels(operation='profile_update').inc()
    return jsonify({
        'message': 'Profile updated successfully',
        'customer': customers_db[customer_id]
    }), 200

@app.route('/api/customers/<customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Get customer profile by ID (admin only through BFF)"""
    if customer_id not in customers_db:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_operations.labels(operation='customer_view').inc()
    return jsonify(customers_db[customer_id]), 200

# ==================== Customer List (Admin) ====================

@app.route('/api/customers', methods=['GET'])
@token_required
def list_customers():
    """List all customers (admin only through BFF)"""
    customer_list = []
    for customer_id, customer in customers_db.items():
        customer_list.append({
            'id': customer_id,
            'email': customer['email'],
            'name': customer['name'],
            'phone': customer['phone'],
            'city': customer['city'],
            'membership_level': customer['membership_level'],
            'total_orders': customer['total_orders'],
            'total_spent': customer['total_spent'],
            'created_at': customer['created_at']
        })
    
    customer_operations.labels(operation='list_customers').inc()
    return jsonify(customer_list), 200

# ==================== Membership & Analytics ====================

@app.route('/api/customers/me/orders', methods=['GET'])
@token_required
def get_customer_orders():
    """Get current customer's order history"""
    user_email = request.user.get('email')
    
    # This would typically query the order service
    # For now, return empty list
    customer_operations.labels(operation='orders_view').inc()
    return jsonify({
        'customer_email': user_email,
        'orders': [],
        'total_count': 0
    }), 200

@app.route('/api/customers/me/preferences', methods=['GET', 'PUT'])
@token_required
def customer_preferences():
    """Get or update customer preferences"""
    user_email = request.user.get('email')
    
    if request.method == 'GET':
        customer_operations.labels(operation='preferences_view').inc()
        return jsonify({
            'customer_email': user_email,
            'preferences': {
                'notifications_email': True,
                'notifications_sms': False,
                'newsletter': True,
                'language': 'en',
                'currency': 'USD'
            }
        }), 200
    else:  # PUT
        data = request.get_json()
        customer_operations.labels(operation='preferences_update').inc()
        return jsonify({
            'message': 'Preferences updated',
            'preferences': data
        }), 200

# ==================== Loyalty & Rewards ====================

@app.route('/api/customers/me/loyalty', methods=['GET'])
@token_required
def get_loyalty_info():
    """Get customer loyalty/membership info"""
    user_email = request.user.get('email')
    
    customer_operations.labels(operation='loyalty_view').inc()
    return jsonify({
        'customer_email': user_email,
        'membership_level': 'silver',
        'points': 250,
        'tier': 'Silver',
        'benefits': [
            '5% discount on all purchases',
            'Free shipping on orders over $50',
            'Exclusive member-only deals'
        ],
        'next_tier': 'Gold',
        'points_to_next_tier': 750
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
