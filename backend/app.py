#!/usr/bin/env python3
"""
Telegraph Messenger Backend
Real-time Morse code messaging application with Flask-SocketIO
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .config import Config
from .database.connection import init_db
from .auth.jwt import init_jwt
from .routes import register_routes
from .sockets import init_socketio_handlers


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    CORS(app, origins=app.config.get('CORS_ORIGINS', []), supports_credentials=True)

    init_db(app)

    jwt = JWTManager(app)
    init_jwt(jwt)

    register_routes(app)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'telegraph-messenger-backend',
            'version': '1.0.0'
        })

    return app


def create_socketio(app):
    """Create and configure Socket.IO for the Flask app."""
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config.get('CORS_ORIGINS', []),
        logger=True,
        engineio_logger=True,
        async_mode='threading'
    )

    init_socketio_handlers(socketio)
    return socketio


app = create_app()
socketio = create_socketio(app)

if __name__ == '__main__':
    port = int(os.getenv('PORT', app.config.get('PORT', 5000)))
    debug = os.getenv('FLASK_ENV', app.config.get('FLASK_ENV', 'development')) == 'development'

    print('🚀 Starting Telegraph Messenger Backend...')
    print(f"📡 SocketIO server running on {app.config.get('SOCKET_URL', 'ws://localhost:5000')}")
    print(f"🌐 REST API available at http://localhost:{port}")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True,
    )
