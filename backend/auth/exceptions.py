"""
Custom authentication exceptions
"""


class AuthException(Exception):
    """Base authentication exception"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AuthException):
    """Input validation error"""
    def __init__(self, message):
        super().__init__(message, 400)


class UserAlreadyExists(AuthException):
    """User already exists in database"""
    def __init__(self, field='user'):
        message = f'{field.capitalize()} already exists'
        super().__init__(message, 409)


class InvalidCredentials(AuthException):
    """Invalid email/password combination"""
    def __init__(self):
        super().__init__('Invalid email or password', 401)


class UserNotFound(AuthException):
    """User not found in database"""
    def __init__(self):
        super().__init__('User not found', 404)


class TokenExpired(AuthException):
    """JWT token has expired"""
    def __init__(self):
        super().__init__('Token has expired', 401)


class InvalidToken(AuthException):
    """Invalid JWT token"""
    def __init__(self):
        super().__init__('Invalid token', 401)


class Unauthorized(AuthException):
    """User is not authenticated"""
    def __init__(self):
        super().__init__('Authorization required', 401)
