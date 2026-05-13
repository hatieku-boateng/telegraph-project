"""
Configuration settings for Telegraph Messenger Backend
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///telegraph_messenger.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # SocketIO
    SOCKET_URL = os.getenv('SOCKET_URL', f'http://localhost:{PORT}')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    # Morse Settings
    MORSE_DOT_THRESHOLD_MS = int(os.getenv('MORSE_DOT_THRESHOLD_MS', 150))
    MORSE_LETTER_GAP_MS = int(os.getenv('MORSE_LETTER_GAP_MS', 400))
    MORSE_WORD_GAP_MS = int(os.getenv('MORSE_WORD_GAP_MS', 1000))

    # Audio Settings
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 44100))
    AUDIO_GAIN = float(os.getenv('AUDIO_GAIN', 100.0))

    # ML Settings
    SPIKE_FACTOR = float(os.getenv('SPIKE_FACTOR', 3.0))
    NOISE_SMOOTH = float(os.getenv('NOISE_SMOOTH', 0.997))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Ensure production has proper secrets
    @property
    def SECRET_KEY(self):
        key = os.getenv('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable is required in production")
        return key

    @property
    def JWT_SECRET_KEY(self):
        key = os.getenv('JWT_SECRET_KEY')
        if not key:
            raise ValueError("JWT_SECRET_KEY environment variable is required in production")
        return key

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}