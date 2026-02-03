"""
Authentication Service
Handles user login, JWT token generation, and user management
"""
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
from pathlib import Path
import time

app = Flask(__name__)

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
TOKEN_EXPIRY = 24  # hours

# Prometheus metrics
login_attempts = Counter('auth_login_attempts_total', 'Total login attempts', ['status'])
token_refreshes = Counter('auth_token_refreshes_total', 'Total token refreshes')
rbac_denials = Counter('auth_rbac_denials_total', 'RBAC access denials', ['role', 'resource'])

# Persistent SQLite DB for users (lightweight, file-based)
DATA_DIR = Path(__file__).resolve().parent
# Use a persistent data subdirectory so we can mount it from the host/container
DATA_DIR_PERSIST = DATA_DIR / 'data'
DB_PATH = DATA_DIR_PERSIST / 'auth.db'
AUDIT_LOG = DATA_DIR_PERSIST / 'user_actions.log'

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # ensure data directory exists
    DATA_DIR_PERSIST.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Ensure default admin/customer users exist
    def ensure_user(email, name, password, role):
        cur.execute('SELECT id FROM users WHERE email=?', (email,))
        if not cur.fetchone():
            cur.execute('INSERT INTO users (name,email,password_hash,role,active,created_at) VALUES (?,?,?,?,?,?)',
                        (name, email, generate_password_hash(password), role, 1, datetime.now().isoformat()))
            conn.commit()

    ensure_user('admin@supermarket.com', 'Admin User', 'admin123', 'admin')
    ensure_user('customer@supermarket.com', 'Customer User', 'customer123', 'customer')
    conn.close()

def row_to_user(row):
    if not row:
        return None
    return {
        'id': str(row['id']),
        'name': row['name'],
        'email': row['email'],
        'password_hash': row['password_hash'],
        'role': row['role'],
        'active': bool(row['active']),
        'created_at': row['created_at']
    }

def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email=?', (email,))
    row = cur.fetchone()
    conn.close()
    return row_to_user(row)

def get_user_by_id(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_user(row)

def list_users_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users ORDER BY id')
    rows = cur.fetchall()
    conn.close()
    return [
        {
            'id': str(r['id']),
            'name': r['name'],
            'email': r['email'],
            'role': r['role'],
            'active': bool(r['active']),
            'created_at': r['created_at']
        } for r in rows
    ]

def create_user_db(email, name, password, role):
    conn = get_db()
    cur = conn.cursor()
    pw_hash = generate_password_hash(password)
    created_at = datetime.now().isoformat()
    cur.execute('INSERT INTO users (name,email,password_hash,role,active,created_at) VALUES (?,?,?,?,?,?)',
                (name, email, pw_hash, role, 1, created_at))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return str(user_id)

def update_user_db(user_id, data):
    user = get_user_by_id(user_id)
    if not user:
        return None
    conn = get_db()
    cur = conn.cursor()
    fields = []
    values = []
    if 'name' in data:
        fields.append('name=?'); values.append(data['name'])
    if 'role' in data:
        fields.append('role=?'); values.append(data['role'])
    if 'active' in data:
        fields.append('active=?'); values.append(1 if data['active'] else 0)
    if 'password' in data and data['password']:
        fields.append('password_hash=?'); values.append(generate_password_hash(data['password']))

    if fields:
        sql = 'UPDATE users SET ' + ','.join(fields) + ' WHERE id=?'
        values.append(user_id)
        cur.execute(sql, tuple(values))
        conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def delete_user_db(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return False
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    return True

def log_user_action(actor_email, action, target, details=''):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, 'a') as f:
        f.write(f"{datetime.now().isoformat()} | {actor_email} | {action} | {target} | {details}\n")

# Role-based access control
RBAC = {
    'admin': {
        'tabs': ['home', 'products', 'cart', 'orders', 'inventory', 'admin', 'monitoring'],
        'api_permissions': ['*'],
        'user_management': True,
        'role_management': True
    },
    'customer': {
        'tabs': ['home', 'products', 'cart', 'orders'],
        'api_permissions': [
            '/api/products',
            '/api/inventory',
            '/api/orders',
            '/monitoring'
        ],
        'user_management': False,
        'role_management': False
    }
}

# Metrics
request_count = Counter('auth_requests_total', 'Total auth requests', ['endpoint', 'method'])
request_duration = Histogram('auth_request_duration_seconds', 'Request duration', ['endpoint'])

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        request_duration.labels(endpoint=request.path).observe(duration)
    request_count.labels(endpoint=request.path, method=request.method).inc()
    # CORS: allow origins from env var for production; default to '*' for development
    allowed = os.getenv('ALLOWED_ORIGINS', '*')
    response.headers['Access-Control-Allow-Origin'] = allowed
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# Utility functions
def generate_token(user_id, email, role):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
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
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(required_role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user.get('role') != required_role and request.user.get('role') != 'admin':
                rbac_denials.labels(role=request.user.get('role'), resource=request.path).inc()
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ==================== Authentication Endpoints ====================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'auth-service', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        login_attempts.labels(status='failed').inc()
        return jsonify({'error': 'Email and password required'}), 400
    
    user = get_user_by_email(email)
    if not user or not check_password_hash(user['password_hash'], password):
        login_attempts.labels(status='failed').inc()
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user['active']:
        login_attempts.labels(status='failed').inc()
        return jsonify({'error': 'User account is inactive'}), 403
    
    token = generate_token(user['id'], user['email'], user['role'])
    login_attempts.labels(status='success').inc()
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify():
    """Verify token and get current user info"""
    user = get_user_by_email(request.user['email'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        },
        'permissions': RBAC.get(user['role'], {})
    }), 200

@app.route('/api/auth/permissions', methods=['GET'])
@token_required
def get_permissions():
    """Get user permissions based on role"""
    role = request.user.get('role')
    permissions = RBAC.get(role, {})
    
    return jsonify({
        'role': role,
        'permissions': permissions,
        'accessible_tabs': permissions.get('tabs', [])
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Simple root to aid browser checks"""
    return jsonify({'service': 'auth-service', 'endpoints': ['/health', '/api/auth/login', '/api/auth/verify', '/api/auth/permissions']}), 200

@app.route('/api/auth/refresh', methods=['POST'])
@token_required
def refresh():
    """Refresh token"""
    user = get_user_by_email(request.user['email'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    new_token = generate_token(user['id'], user['email'], user['role'])
    token_refreshes.inc()
    
    return jsonify({'token': new_token}), 200

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout endpoint (stateless - just returns success)"""
    return jsonify({'message': 'Logged out successfully'}), 200

# ==================== User Management (Admin Only) ====================

@app.route('/api/users', methods=['GET'])
@token_required
@role_required('admin')
def get_users():
    """Get all users (admin only)"""
    users_list = list_users_db()
    return jsonify(users_list), 200

@app.route('/api/users', methods=['POST'])
@token_required
@role_required('admin')
def create_user():
    """Create new user (admin only)"""
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    role = data.get('role', 'customer')
    
    if not email or not name or not password:
        return jsonify({'error': 'Email, name, and password required'}), 400
    
    if get_user_by_email(email):
        return jsonify({'error': 'User already exists'}), 409
    
    if role not in RBAC:
        return jsonify({'error': f'Invalid role. Must be one of: {list(RBAC.keys())}'}), 400
    
    # create in DB
    user_id = create_user_db(email, name, password, role)
    # audit log
    actor = request.user.get('email')
    log_user_action(actor, 'create_user', email, f'role={role}')

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'role': role
        }
    }), 201

@app.route('/api/users/<user_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_user(user_id):
    """Update user (admin only)"""
    data = request.get_json()
    
    # validate role if provided
    if 'role' in data and data['role'] not in RBAC:
        return jsonify({'error': f'Invalid role. Must be one of: {list(RBAC.keys())}'}), 400

    updated = update_user_db(user_id, data)
    if not updated:
        return jsonify({'error': 'User not found'}), 404

    actor = request.user.get('email')
    log_user_action(actor, 'update_user', updated['email'], f'fields={list(data.keys())}')

    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': updated['id'],
            'name': updated['name'],
            'email': updated['email'],
            'role': updated['role'],
            'active': updated['active']
        }
    }), 200

@app.route('/api/users/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    """Delete user (admin only)"""
    target = get_user_by_id(user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    success = delete_user_db(user_id)
    if success:
        actor = request.user.get('email')
        log_user_action(actor, 'delete_user', target['email'])
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete user'}), 500

# ==================== Role Management ====================

@app.route('/api/roles', methods=['GET'])
@token_required
@role_required('admin')
def get_roles():
    """Get all available roles (admin only)"""
    roles_list = []
    for role_name, permissions in RBAC.items():
        roles_list.append({
            'name': role_name,
            'permissions': permissions
        })
    return jsonify(roles_list), 200


@app.route('/api/audit', methods=['GET'])
@token_required
@role_required('admin')
def get_audit():
    """Return recent audit log lines (admin only). Query param `lines` controls number of lines."""
    lines = int(request.args.get('lines', '200'))
    if not AUDIT_LOG.exists():
        return jsonify({'logs': []}), 200
    try:
        with open(AUDIT_LOG, 'r') as f:
            all_lines = f.readlines()
            tail = all_lines[-lines:]
        return jsonify({'logs': [l.strip() for l in tail]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize DB and start service
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=False)
