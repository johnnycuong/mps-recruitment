from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

from src.models.user import db, User, UserRole

auth_bp = Blueprint('auth', __name__)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# Role-based access control decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': 'Permission denied!'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists!'}), 409
    
    # Create new user
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    try:
        role = UserRole(data.get('role', 'RECRUITER'))
    except ValueError:
        return jsonify({'message': 'Invalid role!'}), 400
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        full_name=data['full_name'],
        phone=data.get('phone', ''),
        role=role
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password!'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated!'}), 403
    
    if check_password_hash(user.password_hash, data['password']):
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.value
            }
        })
    
    return jsonify({'message': 'Invalid password!'}), 401

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'full_name': current_user.full_name,
        'phone': current_user.phone,
        'role': current_user.role.value,
        'created_at': current_user.created_at.isoformat()
    })

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    if 'full_name' in data:
        current_user.full_name = data['full_name']
    
    if 'phone' in data:
        current_user.phone = data['phone']
    
    if 'password' in data:
        current_user.password_hash = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully!'})

@auth_bp.route('/users', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def get_users(current_user):
    users = User.query.all()
    
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }
        output.append(user_data)
    
    return jsonify({'users': output})

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def get_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'role': user.role.value,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }
    
    return jsonify({'user': user_data})

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@role_required([UserRole.ADMIN])
def update_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    
    if 'email' in data:
        user.email = data['email']
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
        except ValueError:
            return jsonify({'message': 'Invalid role!'}), 400
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'password' in data:
        user.password_hash = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully!'})

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN])
def delete_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'message': 'Cannot delete yourself!'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully!'})
