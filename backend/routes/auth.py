"""
Authentication routes with production-ready error handling
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..auth.middleware import get_jwt_identity_int, get_current_user

from ..database.connection import get_db
from ..models import User
from ..auth.utils import (
    TokenManager,
    PasswordManager,
    handle_auth_errors
)
from ..auth.validation import EmailValidator, UsernameValidator, PasswordValidator
from ..auth.middleware import get_current_user
from ..auth.exceptions import (
    AuthException,
    ValidationError,
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound,
    Unauthorized
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.errorhandler(AuthException)
def handle_auth_exception(error):
    """Global error handler for authentication exceptions"""
    return jsonify({
        'error': type(error).__name__,
        'message': error.message
    }), error.status_code


@auth_bp.route('/signup', methods=['POST'])
@handle_auth_errors
def signup():
    """
    User registration endpoint
    
    Request body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Returns:
        201: User created successfully with tokens
        400: Validation error
        409: User already exists
    """
    data = request.get_json()

    if not data:
        raise ValidationError('No data provided')

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validation
    EmailValidator.validate(email)
    UsernameValidator.validate(username)
    PasswordValidator.validate(password)

    db = get_db()

    # Check if user already exists
    if db.query(User).filter(User.username == username).first():
        raise UserAlreadyExists('username')

    if db.query(User).filter(User.email == email).first():
        raise UserAlreadyExists('email')

    # Create new user
    password_hash = PasswordManager.hash_password(password)
    avatar_initials = username[:2].upper()

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        avatar_initials=avatar_initials,
        display_name=username,
        email_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create tokens
    tokens = TokenManager.create_token_pair(user.id)

    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(include_sensitive=True),
        **tokens
    }), 201


@auth_bp.route('/login', methods=['POST'])
@handle_auth_errors
def login():
    """
    User login endpoint
    
    Request body:
    {
        "email": "string",
        "password": "string"
    }
    
    Returns:
        200: Login successful with tokens
        400: Validation error
        401: Invalid credentials
    """
    data = request.get_json()

    if not data:
        raise ValidationError('No data provided')

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        raise ValidationError('Email and password are required')

    db = get_db()
    user = db.query(User).filter(User.email == email).first()

    if not user or not PasswordManager.verify_password(password, user.password_hash):
        raise InvalidCredentials()

    if not user.is_active:
        raise ValidationError('Account is disabled')

    # Update login info
    user.update_last_login()
    user.set_online()
    db.commit()

    # Create tokens
    tokens = TokenManager.create_token_pair(user.id)

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_sensitive=True),
        **tokens
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_auth_errors
def refresh():
    """
    Refresh access token using refresh token
    
    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    user_id = get_jwt_identity_int()
    
    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise UserNotFound()
    
    if not user.is_active:
        raise ValidationError('Account is disabled')

    access_token = TokenManager.create_access_token(user.id)

    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@handle_auth_errors
def get_profile():
    """
    Get current user profile
    
    Returns:
        200: Current user profile data
        404: User not found
    """
    user = get_current_user()
    return jsonify(user.to_dict_full()), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@handle_auth_errors
def update_profile():
    """
    Update current user profile
    
    Request body:
    {
        "username": "string (optional)",
        "email": "string (optional)",
        "display_name": "string (optional)",
        "bio": "string (optional)"
    }
    
    Returns:
        200: Profile updated successfully
        400: Validation error
        409: Username or email already taken
        404: User not found
    """
    user = get_current_user()
    data = request.get_json()

    if not data:
        raise ValidationError('No data provided')

    db = get_db()

    # Validate and update username
    if 'username' in data:
        new_username = data['username'].strip()
        UsernameValidator.validate(new_username)
        
        if new_username != user.username:
            existing = db.query(User).filter(
                User.username == new_username,
                User.id != user.id
            ).first()
            if existing:
                raise UserAlreadyExists('username')
            
            user.username = new_username
            user.avatar_initials = new_username[:2].upper()

    # Validate and update email
    if 'email' in data:
        new_email = data['email'].strip()
        EmailValidator.validate(new_email)
        
        if new_email != user.email:
            existing = db.query(User).filter(
                User.email == new_email,
                User.id != user.id
            ).first()
            if existing:
                raise UserAlreadyExists('email')
            
            user.email = new_email
            user.email_verified = False

    # Update display_name and bio
    if 'display_name' in data:
        display_name = data['display_name'].strip()
        if len(display_name) > 100:
            raise ValidationError('Display name is too long (max 100 characters)')
        user.display_name = display_name

    if 'bio' in data:
        bio = data['bio'].strip()
        if len(bio) > 500:
            raise ValidationError('Bio is too long (max 500 characters)')
        user.bio = bio

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict_full()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@handle_auth_errors
def change_password():
    """
    Change user password
    
    Request body:
    {
        "old_password": "string",
        "new_password": "string"
    }
    
    Returns:
        200: Password changed successfully
        400: Validation error
        401: Incorrect old password
    """
    user = get_current_user()
    data = request.get_json()

    if not data:
        raise ValidationError('No data provided')

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        raise ValidationError('Old and new password are required')

    # Verify old password
    if not PasswordManager.verify_password(old_password, user.password_hash):
        raise InvalidCredentials()

    # Validate new password
    PasswordValidator.validate(new_password)

    if old_password == new_password:
        raise ValidationError('New password must be different from old password')

    # Update password
    user.password_hash = PasswordManager.hash_password(new_password)
    user.updated_at = datetime.utcnow()

    db = get_db()
    db.commit()

    return jsonify({
        'message': 'Password changed successfully'
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@handle_auth_errors
def logout():
    """
    User logout - mark as offline
    
    Returns:
        200: Logged out successfully
    """
    user = get_current_user()
    user.set_offline()
    
    db = get_db()
    db.commit()

    return jsonify({
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/verify-email', methods=['POST'])
@jwt_required()
@handle_auth_errors
def verify_email():
    """
    Verify user email (placeholder - implement with actual verification logic)
    
    Request body:
    {
        "token": "string"
    }
    
    Returns:
        200: Email verified
    """
    user = get_current_user()
    
    if user.email_verified:
        raise ValidationError('Email is already verified')
    
    # TODO: Implement email verification token validation
    user.email_verified = True
    
    db = get_db()
    db.commit()

    return jsonify({
        'message': 'Email verified successfully'
    }), 200


@auth_bp.route('/resend-verification', methods=['POST'])
@handle_auth_errors
def resend_verification():
    """
    Resend email verification (placeholder)
    
    Request body:
    {
        "email": "string"
    }
    
    Returns:
        200: Verification email sent
    """
    data = request.get_json()
    
    if not data:
        raise ValidationError('No data provided')
    
    email = data.get('email', '').strip()
    EmailValidator.validate(email)
    
    db = get_db()
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise UserNotFound()
    
    if user.email_verified:
        raise ValidationError('Email is already verified')
    
    # TODO: Implement verification email sending
    
    return jsonify({
        'message': 'Verification email sent successfully'
    }), 200


@auth_bp.route('/status', methods=['GET'])
@jwt_required(optional=True)
@handle_auth_errors
def auth_status():
    """
    Check authentication status
    
    Returns:
        200: Authentication status
    """
    user_id = get_jwt_identity_int()
    
    if user_id is None:
        return jsonify({
            'authenticated': False,
            'user': None
        }), 200
    
    user = get_current_user()
    
    return jsonify({
        'authenticated': True,
        'user': user.to_dict(include_sensitive=True)
    }), 200