"""
Route registration
"""

from flask import Flask
from .auth import auth_bp
from .messages import messages_bp
from .morse import morse_bp

def register_routes(app: Flask):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(morse_bp)