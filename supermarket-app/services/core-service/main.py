"""
Core Service
Business logic for products, inventory, and orders
"""
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from datetime import datetime
import random
import uuid

app = Flask(__name__)

# Prometheus metrics
request_count = Counter('core_service_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('core_service_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
orders_created = Counter('orders_created_total', 'Total orders created')
products_queried = Counter('products_queried_total', 'Total product queries')

# Mock data
products_db = {
    '1': {'id': '1', 'name': 'Milk', 'price': 3.99, 'category': 'Dairy'},
    '2': {'id': '2', 'name': 'Bread', 'price': 2.49, 'category': 'Bakery'},
    '3': {'id': '3', 'name': 'Cheese', 'price': 4.99, 'category': 'Dairy'},
    '4': {'id': '4', 'name': 'Apples', 'price': 1.99, 'category': 'Produce'},
}

orders_db = {}

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
    return jsonify({'status': 'healthy', 'service': 'core-service', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    products_queried.inc()
    return jsonify(list(products_db.values())), 200

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    products_queried.inc()
    if product_id in products_db:
        return jsonify(products_db[product_id]), 200
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    data = request.get_json()
    product_id = str(uuid.uuid4())[:8]
    products_db[product_id] = {
        'id': product_id,
        'name': data.get('name'),
        'price': data.get('price'),
        'category': data.get('category')
    }
    return jsonify(products_db[product_id]), 201

@app.route('/orders', methods=['POST'])
def create_order():
    """Create new order"""
    orders_created.inc()
    data = request.get_json()
    order_id = str(uuid.uuid4())[:8]
    
    order = {
        'id': order_id,
        'items': data.get('items', []),
        'total': sum(item.get('price', 0) * item.get('quantity', 1) for item in data.get('items', [])),
        'status': 'created',
        'created_at': datetime.now().isoformat()
    }
    orders_db[order_id] = order
    return jsonify(order), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    if order_id in orders_db:
        return jsonify(orders_db[order_id]), 200
    return jsonify({'error': 'Order not found'}), 404

@app.route('/inventory', methods=['GET'])
def get_inventory():
    """Get inventory information"""
    inventory = []
    for product_id, product in products_db.items():
        inventory.append({
            'id': product_id,
            'name': product['name'],
            'category': product['category'],
            'price': product['price'],
            'stock': 100,  # Mock stock value
            'reorderLevel': 20
        })
    return jsonify(inventory), 200

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    if order_id not in orders_db:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    orders_db[order_id]['status'] = data.get('status')
    return jsonify(orders_db[order_id]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
