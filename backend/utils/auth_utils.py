import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from models.db_models import User

def generate_token(user_id):
    """
    Generates the Auth Token
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_token(auth_token):
    """
    Decodes the auth token
    """
    try:
        payload = jwt.decode(
            auth_token, 
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'error': 'Bearer token malformed'}), 401
        
        # Also check cookies for httpOnly support
        elif request.cookies.get('auth_token'):
            token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401

        resp = decode_token(token)
        if isinstance(resp, str) and (resp.startswith('Signature') or resp.startswith('Invalid')):
            return jsonify({'success': False, 'error': resp}), 401

        # Check if user exists
        current_user = User.query.get(resp)
        if not current_user:
            return jsonify({'success': False, 'error': 'User not found'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'error': 'Bearer token malformed'}), 401
        elif request.cookies.get('auth_token'):
            token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401

        resp = decode_token(token)
        if isinstance(resp, str) and (resp.startswith('Signature') or resp.startswith('Invalid')):
            return jsonify({'success': False, 'error': resp}), 401

        current_user = User.query.get(resp)
        if not current_user or not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403

        return f(current_user, *args, **kwargs)

    return decorated
