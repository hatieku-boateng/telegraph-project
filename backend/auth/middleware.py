"""
Authentication middleware and decorators
"""

from functools import wraps
from flask import jsonify, request, session as socket_session
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from flask_socketio import emit

from ..database.connection import get_db
from ..models import User
from .exceptions import UserNotFound, Unauthorized, InvalidToken


def require_auth(fn):
    """
    Decorator to require valid JWT authentication and load current user
    
    Usage:
        @require_auth
        def protected_route():
            user = get_current_user()
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def get_jwt_identity_int() -> int:
    """
    Get the current JWT identity as an integer.
    """
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return identity


def get_current_user() -> User:
    """
    Get the current authenticated user from JWT token
    
    Returns:
        User object
        
    Raises:
        UserNotFound: If user not found in database
    """
    try:
        user_id = get_jwt_identity_int()
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise UserNotFound()
        
        return user
    except UserNotFound:
        raise
    except Exception:
        raise UserNotFound()


def get_socket_token(auth_payload=None) -> str:
    """
    Extract JWT from socket auth payload, query string, or Authorization header.
    """
    token = None

    if isinstance(auth_payload, dict):
        token = auth_payload.get('token') or auth_payload.get('access_token')

    if not token:
        token = request.args.get('token')

    authorization = request.headers.get('Authorization', '')
    if not token and authorization.startswith('Bearer '):
        token = authorization.replace('Bearer ', '', 1).strip()

    return token


def authenticate_socket(auth_payload=None) -> User:
    """
    Validate a socket JWT and store the authenticated user in socket session.
    """
    token = get_socket_token(auth_payload)
    if not token:
        raise Unauthorized()

    try:
        decoded = decode_token(token)
    except Exception:
        raise InvalidToken()

    user_id = decoded.get('sub')
    if not user_id:
        raise InvalidToken()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise InvalidToken()

    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFound()

    socket_session['user_id'] = user.id
    return user


def get_socket_user() -> User:
    """
    Get the current authenticated socket user from session.
    """
    user_id = socket_session.get('user_id')
    if not user_id:
        raise Unauthorized()

    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFound()

    return user


def socket_auth_required(fn):
    """
    Decorator to protect socket handlers with JWT authentication.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            get_socket_user()
        except Exception as exc:
            emit('auth_error', {'message': str(exc)})
            return False
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """
    Decorator to require admin user role
    
    Usage:
        @admin_required
        def admin_route():
            pass
    """
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        
        # Check if user has admin role
        if not getattr(user, 'is_admin', False):
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin access required'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def get_token_info() -> dict:
    """
    Get information from current JWT token
    
    Returns:
        Dictionary with token info including user_id, exp, etc.
    """
    from flask_jwt_extended import get_jwt
    
    jwt_data = get_jwt()
    return {
        'user_id': jwt_data.get('sub'),
        'additional_claims': {k: v for k, v in jwt_data.items() if k not in ['sub', 'iat', 'exp', 'jti', 'type']}
    }
