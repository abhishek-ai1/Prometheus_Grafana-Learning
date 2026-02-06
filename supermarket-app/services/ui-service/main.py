"""
UI Service
Frontend server for the supermarket application
"""
from flask import Flask, jsonify, send_from_directory, request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from datetime import datetime
import os
import requests

app = Flask(__name__, static_folder='static', static_url_path='')

# Prometheus metrics
request_count = Counter('ui_service_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('ui_service_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
page_views = Counter('page_views_total', 'Page views', ['page'])

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
    return jsonify({'status': 'healthy', 'service': 'ui-service', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/', methods=['GET'])
def index():
    page_views.labels(page='home').inc()
    return send_from_directory('static', 'index.html')

@app.route('/login', methods=['GET'])
@app.route('/login.html', methods=['GET'])
def login_page():
    page_views.labels(page='login').inc()
    return send_from_directory('static', 'login.html')

@app.route('/register', methods=['GET'])
@app.route('/register.html', methods=['GET'])
def register_page():
    page_views.labels(page='register').inc()
    return send_from_directory('static', 'register.html')


@app.route('/products', methods=['GET'])
def products_page():
    page_views.labels(page='products').inc()
    return send_from_directory('static', 'products.html')

@app.route('/cart', methods=['GET'])
def cart_page():
    """Shopping cart page"""
    page_views.labels(page='cart').inc()
    return send_from_directory('static', 'cart.html')

@app.route('/orders', methods=['GET'])
def orders_page():
    page_views.labels(page='orders').inc()
    return send_from_directory('static', 'orders.html')

@app.route('/admin', methods=['GET'])
def admin_page():
    """Admin dashboard for product and inventory management"""
    page_views.labels(page='admin').inc()
    return send_from_directory('static', 'admin.html')

@app.route('/inventory', methods=['GET'])
def inventory_page():
    """Inventory management page"""
    page_views.labels(page='inventory').inc()
    return send_from_directory('static', 'inventory.html')

@app.route('/monitoring', methods=['GET'])
def monitoring_page():
    """System monitoring and status dashboard"""
    page_views.labels(page='monitoring').inc()
    return send_from_directory('static', 'monitoring.html')


@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_api(path):
    """Proxy API requests from the UI to the internal BFF service.

    This allows the browser to call relative paths (same origin) and
    the UI service will forward them to the `bff-service` inside Docker.
    Useful for Codespaces / forwarded ports where `localhost` from the
    browser does not map to service containers.
    """
    # Build target URL for internal BFF
    # Use global BFF_SERVICE_URL variable (loaded from env) to support local testing
    target_url = f"{BFF_SERVICE_URL}/api/{path}"

    # Handle preflight
    if request.method == 'OPTIONS':
        resp = Response(status=200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return resp

    try:
        # Forward the request
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            params=request.args,
            data=request.get_data(),
            timeout=10
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/config', methods=['GET'])
def get_config():
    """Get UI configuration"""
    return jsonify({
        'api_base_url': os.getenv('API_BASE_URL', 'http://bff-service:5000'),
        'environment': os.getenv('ENVIRONMENT', 'production')
    }), 200

# API Proxy routes - Forward requests to BFF service
BFF_SERVICE_URL = os.getenv('BFF_SERVICE_URL', 'http://bff-service:5000')
PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')


@app.route('/api/health', methods=['GET'])
def api_health():
    """Aggregate health status for all services (queried server-side).
    This avoids the browser needing to call localhost: ports that are unreachable
    when the app is accessed from outside the container (e.g., Codespaces).
    """
    services = [
        {'name': 'BFF Service', 'url': os.getenv('BFF_SERVICE_URL', 'http://bff-service:5000'), 'port': 5000},
        {'name': 'Core Service', 'url': os.getenv('CORE_SERVICE_URL', 'http://core-service:5001'), 'port': 5001},
        {'name': 'UI Service', 'url': os.getenv('UI_SERVICE_URL', 'http://ui-service:5002'), 'port': 5002},
        {'name': 'Prometheus', 'url': os.getenv('PROMETHEUS_URL', 'http://prometheus:9090'), 'port': 9090},
        {'name': 'Grafana', 'url': os.getenv('GRAFANA_URL', 'http://grafana:3000'), 'port': 3000}
    ]

    results = []
    for s in services:
        status = 'unhealthy'
        try:
            # Prefer /health if available
            try:
                r = requests.get(f"{s['url']}/health", timeout=2)
                if r.ok:
                    status = 'healthy'
                else:
                    # If /health exists but is not OK (e.g., 404), try sensible fallbacks
                    try:
                        if s['name'] == 'Prometheus':
                            r2 = requests.get(f"{s['url']}/metrics", timeout=2)
                            if r2.status_code == 200:
                                status = 'healthy'
                        else:
                            r2 = requests.get(s['url'], timeout=2)
                            if r2.ok:
                                status = 'healthy'
                    except Exception:
                        status = 'unhealthy'
            except Exception:
                # If requesting /health raised an exception, try fallbacks
                try:
                    if s['name'] == 'Prometheus':
                        r = requests.get(f"{s['url']}/metrics", timeout=2)
                        if r.status_code == 200:
                            status = 'healthy'
                    else:
                        r = requests.get(s['url'], timeout=2)
                        if r.ok:
                            status = 'healthy'
                except Exception:
                    status = 'unhealthy'
        except Exception:
            status = 'unhealthy'

        results.append({'name': s['name'], 'status': status, 'port': s['port'], 'url': s['url']})

    return jsonify(results), 200

@app.route('/api/products', methods=['GET', 'POST'])
def proxy_products():
    """Proxy products endpoint to BFF service"""
    try:
        if request.method == 'POST':
            response = requests.post(f'{BFF_SERVICE_URL}/api/products', json=request.json, timeout=5)
        else:
            response = requests.get(f'{BFF_SERVICE_URL}/api/products', timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/api/prometheus/query', methods=['GET'])
def prometheus_query():
    """Proxy a Prometheus instant query. Query string param: `query`"""
    q = request.args.get('query')
    if not q:
        return jsonify({'error': 'missing query parameter'}), 400
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': q}, timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/api/prometheus/query_range', methods=['GET'])
def prometheus_query_range():
    """Proxy a Prometheus range query. Params: query, start, end, step"""
    q = request.args.get('query')
    start = request.args.get('start')
    end = request.args.get('end')
    step = request.args.get('step', '30s')
    if not q or not start or not end:
        return jsonify({'error': 'missing query/start/end parameters'}), 400
    try:
        params = {'query': q, 'start': start, 'end': end, 'step': step}
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/inventory', methods=['GET'])
def proxy_inventory():
    """Proxy inventory endpoint to BFF service"""
    try:
        response = requests.get(f'{BFF_SERVICE_URL}/api/inventory', timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/orders', methods=['GET', 'POST'])
def proxy_orders():
    """Proxy orders endpoint to BFF service"""
    try:
        if request.method == 'POST':
            response = requests.post(f'{BFF_SERVICE_URL}/api/orders', json=request.json, timeout=5)
        else:
            response = requests.get(f'{BFF_SERVICE_URL}/api/orders', timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
