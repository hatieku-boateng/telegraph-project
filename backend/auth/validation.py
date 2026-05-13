"""
Input validation utilities for authentication
"""

import re
from .exceptions import ValidationError


class EmailValidator:
    """Email validation"""
    PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        if not email or not isinstance(email, str):
            raise ValidationError('Email is required')

        email = email.strip()
        
        if len(email) > 255:
            raise ValidationError('Email is too long')

        if not re.match(EmailValidator.PATTERN, email):
            raise ValidationError('Invalid email format')

        return True


class UsernameValidator:
    """Username validation"""
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    PATTERN = r'^[a-zA-Z0-9_-]+$'

    @staticmethod
    def validate(username: str) -> bool:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        if not username or not isinstance(username, str):
            raise ValidationError('Username is required')

        username = username.strip()

        if len(username) < UsernameValidator.MIN_LENGTH:
            raise ValidationError(
                f'Username must be at least {UsernameValidator.MIN_LENGTH} characters'
            )

        if len(username) > UsernameValidator.MAX_LENGTH:
            raise ValidationError(
                f'Username must not exceed {UsernameValidator.MAX_LENGTH} characters'
            )

        if not re.match(UsernameValidator.PATTERN, username):
            raise ValidationError(
                'Username can only contain letters, numbers, hyphens, and underscores'
            )

        return True


class PasswordValidator:
    """Password validation"""
    MIN_LENGTH = 6
    MAX_LENGTH = 128

    @staticmethod
    def validate(password: str, strict: bool = False) -> bool:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            strict: If True, require uppercase, lowercase, number, special char
            
        Returns:
            True if valid, raises ValidationError otherwise
        """
        if not password or not isinstance(password, str):
            raise ValidationError('Password is required')

        if len(password) < PasswordValidator.MIN_LENGTH:
            raise ValidationError(
                f'Password must be at least {PasswordValidator.MIN_LENGTH} characters'
            )

        if len(password) > PasswordValidator.MAX_LENGTH:
            raise ValidationError(
                f'Password must not exceed {PasswordValidator.MAX_LENGTH} characters'
            )

        if strict:
            has_upper = re.search(r'[A-Z]', password)
            has_lower = re.search(r'[a-z]', password)
            has_digit = re.search(r'\d', password)
            has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

            if not all([has_upper, has_lower, has_digit, has_special]):
                raise ValidationError(
                    'Password must contain uppercase, lowercase, number, and special character'
                )

        return True
