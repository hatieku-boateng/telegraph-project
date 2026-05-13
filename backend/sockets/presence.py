"""
Presence socket event handlers for Telegraph Messenger.
"""

from datetime import datetime
from flask_socketio import emit, disconnect
from flask import request

from ..auth.middleware import authenticate_socket, get_socket_user, socket_auth_required
from ..database.connection import get_db
from ..models import User


def register_presence_handlers(socketio):
    """Register presence and authentication socket handlers."""

    @socketio.on('connect')
    def handle_connect(auth):
        """Authenticate socket connection with JWT token."""
        try:
            user = authenticate_socket(auth)
            user.set_online()
            db = get_db()
            db.add(user)
            db.commit()

            emit('authenticated', {
                'user': user.to_dict(),
                'status': 'success'
            })

            emit('user_online', user.to_dict(), broadcast=True, skip_sid=request.sid)
        except Exception as exc:
            print(f"Socket authentication failed: {exc}")
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle socket disconnection and update presence."""
        try:
            user = get_socket_user()
            user.set_offline()
            db = get_db()
            db.add(user)
            db.commit()

            emit('user_offline', {
                'user_id': user.id,
                'username': user.username
            }, broadcast=True, skip_sid=request.sid)
        except Exception:
            pass

    @socketio.on('authenticate')
    def handle_authenticate(data):
        """Authenticate a connected client after connection."""
        try:
            user = authenticate_socket(data)
            user.set_online()
            db = get_db()
            db.add(user)
            db.commit()

            emit('authenticated', {
                'user': user.to_dict(),
                'status': 'success'
            })
            emit('user_online', user.to_dict(), broadcast=True, skip_sid=request.sid)
        except Exception as exc:
            emit('auth_error', {'message': str(exc)})
            disconnect()

    @socketio.on('get_online_users')
    @socket_auth_required
    def handle_get_online_users():
        """Return the current list of online users."""
        try:
            db = get_db()
            users = db.query(User).filter(User.is_online == True).all()
            emit('online_users', [user.to_dict() for user in users])
        except Exception as exc:
            emit('error', {'message': 'Unable to fetch online users'})
