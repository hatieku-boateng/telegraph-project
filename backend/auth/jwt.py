"""
JWT authentication utilities
"""

from flask_jwt_extended import JWTManager
from flask import jsonify

def init_jwt(jwt: JWTManager):
    """Initialize JWT manager with callbacks"""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please log in again'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token is invalid'
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'error': 'Missing authorization header',
            'message': 'Authorization header is required'
        }), 401

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT identity"""
        from ..database.connection import get_db
        from ..models import User

        identity = jwt_data["sub"]
        try:
            identity = int(identity)
        except (TypeError, ValueError):
            return None

        db = get_db()
        user = db.query(User).filter(User.id == identity).first()

        return user

    @jwt.user_lookup_error_loader
    def user_lookup_error_callback(_jwt_header, jwt_data):
        return jsonify({
            'error': 'User not found',
            'message': 'The user associated with this token was not found'
        }), 404