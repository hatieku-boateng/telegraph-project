"""
Authentication utilities - JWT token management and password hashing
"""

from datetime import datetime, timedelta
from functools import wraps

import bcrypt
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token as jwt_create_access_token,
    create_refresh_token as jwt_create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request
)

from .exceptions import InvalidToken, Unauthorized


class TokenManager:
    """JWT token creation and management"""

    @staticmethod
    def create_access_token(user_id: int, additional_claims: dict = None) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID to include in token
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT access token string
        """
        claims = {'user_id': user_id}
        if additional_claims:
            claims.update(additional_claims)
        return jwt_create_access_token(identity=str(user_id), additional_claims=claims)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Create JWT refresh token
        
        Args:
            user_id: User ID to include in token
            
        Returns:
            JWT refresh token string
        """
        return jwt_create_refresh_token(identity=str(user_id))

    @staticmethod
    def create_token_pair(user_id: int) -> dict:
        """
        Create both access and refresh tokens
        
        Args:
            user_id: User ID for token generation
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        return {
            'access_token': TokenManager.create_access_token(user_id),
            'refresh_token': TokenManager.create_refresh_token(user_id),
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour in seconds
        }

    @staticmethod
    def get_user_id_from_token() -> int:
        """
        Extract user ID from current JWT token
        
        Returns:
            User ID from token identity
            
        Raises:
            InvalidToken: If no valid token in request
        """
        try:
            user_id = get_jwt_identity()
            return int(user_id)
        except (TypeError, ValueError, Exception):
            raise InvalidToken()


class PasswordManager:
    """Password hashing and verification using bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        if not isinstance(password, str):
            raise ValueError('Password must be a string')

        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a plain text password against bcrypt hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password to check against

        Returns:
            True if password matches hash, False otherwise
        """
        try:
            if not isinstance(password, str) or not isinstance(password_hash, str):
                return False

            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False


def jwt_required_custom(optional: bool = False):
    """
    Custom JWT requirement decorator with consistent error handling
    
    Args:
        optional: If True, token is optional but validated if present
        
    Returns:
        Decorator function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
            except Exception as e:
                if optional and 'Authorization' not in request.headers:
                    return fn(*args, **kwargs)
                raise Unauthorized()
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def handle_auth_errors(fn):
    """
    Decorator to handle authentication exceptions and return proper JSON responses
    
    Args:
        fn: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            from .exceptions import AuthException
            if isinstance(e, AuthException):
                return jsonify({
                    'error': type(e).__name__,
                    'message': e.message
                }), e.status_code
            # Re-raise unexpected exceptions
            raise
    return wrapper
