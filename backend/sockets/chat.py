"""
Chat socket event handlers for Telegraph Messenger.
"""

from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room

from ..auth.middleware import get_socket_user, socket_auth_required
from ..database.connection import get_db
from ..models import Message, Conversation, ConversationParticipant


def register_chat_handlers(socketio):
    """Register real-time chat handlers."""

    @socketio.on('join_conversation')
    @socket_auth_required
    def handle_join_conversation(data):
        """Join a conversation room."""
        user = get_socket_user()
        conversation_id = data.get('conversation_id') if isinstance(data, dict) else None
        if isinstance(conversation_id, str) and conversation_id.isdigit():
            conversation_id = int(conversation_id)

        if not conversation_id:
            emit('error', {'message': 'conversation_id is required'})
            return

        db = get_db()
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user.id
        ).first()

        if not participant:
            emit('error', {'message': 'Access denied to conversation'})
            return

        join_room(str(conversation_id))
        emit('joined_conversation', {
            'conversation_id': conversation_id,
            'status': 'success'
        })

    @socketio.on('leave_conversation')
    @socket_auth_required
    def handle_leave_conversation(data):
        """Leave a conversation room."""
        user = get_socket_user()
        conversation_id = data.get('conversation_id') if isinstance(data, dict) else None
        if isinstance(conversation_id, str) and conversation_id.isdigit():
            conversation_id = int(conversation_id)

        if not conversation_id:
            emit('error', {'message': 'conversation_id is required'})
            return

        leave_room(str(conversation_id))
        emit('left_conversation', {
            'conversation_id': conversation_id,
            'status': 'success'
        })

    @socketio.on('send_message')
    @socket_auth_required
    def handle_send_message(data):
        """Send a message to a conversation room."""
        user = get_socket_user()
        if not isinstance(data, dict):
            emit('error', {'message': 'Invalid payload'})
            return

        conversation_id = data.get('conversation_id')
        if isinstance(conversation_id, str) and conversation_id.isdigit():
            conversation_id = int(conversation_id)

        content = (data.get('content') or '').strip()
        morse_code = data.get('morse_code')
        message_type = data.get('message_type', 'text')
        input_method = data.get('input_method', 'text')

        if not conversation_id:
            emit('error', {'message': 'conversation_id is required'})
            return

        if not content and not morse_code:
            emit('error', {'message': 'Message content or morse_code is required'})
            return

        db = get_db()
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user.id
        ).first()

        if not participant:
            emit('error', {'message': 'Access denied to conversation'})
            return

        message = Message(
            conversation_id=conversation_id,
            sender_id=user.id,
            content=content,
            morse_code=morse_code,
            message_type=message_type,
            input_method=input_method
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            db.commit()

        emit('message_received', message.to_dict(), room=str(conversation_id))

    @socketio.on('typing_start')
    @socket_auth_required
    def handle_typing_start(data):
        """Notify conversation that a user started typing."""
        user = get_socket_user()
        conversation_id = data.get('conversation_id') if isinstance(data, dict) else None

        if not conversation_id:
            return

        emit('typing_indicator', {
            'user_id': user.id,
            'conversation_id': conversation_id,
            'is_typing': True
        }, room=str(conversation_id), skip_sid=request.sid)

    @socketio.on('typing_stop')
    @socket_auth_required
    def handle_typing_stop(data):
        """Notify conversation that a user stopped typing."""
        user = get_socket_user()
        conversation_id = data.get('conversation_id') if isinstance(data, dict) else None

        if not conversation_id:
            return

        emit('typing_indicator', {
            'user_id': user.id,
            'conversation_id': conversation_id,
            'is_typing': False
        }, room=str(conversation_id), skip_sid=request.sid)
