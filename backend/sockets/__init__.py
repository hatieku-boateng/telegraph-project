"""
Socket.IO handler registration for Telegraph Messenger.
"""

from flask_socketio import emit

from .chat import register_chat_handlers
from .presence import register_presence_handlers


def init_socketio_handlers(socketio):
    """Register all Socket.IO handler modules."""
    register_presence_handlers(socketio)
    register_chat_handlers(socketio)

    @socketio.on_error_default
    def handle_socket_error(error):
        print(f"Socket error: {error}")
        emit('socket_error', {'message': 'A server error occurred'})
