"""
Message and conversation routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..auth.middleware import get_jwt_identity_int
from sqlalchemy import desc

from ..database.connection import get_db
from ..models import User, Message
from ..services.chat_service import (
    chat_service,
    ChatAccessError,
    ChatNotFoundError,
    ChatValidationError,
)

messages_bp = Blueprint('messages', __name__, url_prefix='/api')

@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get user's conversations"""
    current_user_id = get_jwt_identity_int()
    db = get_db()

    conversations = chat_service.get_user_conversations(current_user_id)

    results = []
    for conv in conversations:
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(desc(Message.created_at)).first()

        conv_data = conv.to_dict()
        conv_data['last_message'] = last_message.to_dict() if last_message else None
        results.append(conv_data)

    results.sort(key=lambda x: x.get('last_message', {}).get('created_at', ''), reverse=True)
    return jsonify(results), 200

@messages_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new conversation"""
    current_user_id = get_jwt_identity_int()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    participant_ids = data.get('participant_ids', [])
    if not isinstance(participant_ids, list):
        return jsonify({'error': 'participant_ids must be a list'}), 400

    try:
        participant_ids = [int(pid) for pid in participant_ids]
    except (TypeError, ValueError):
        return jsonify({'error': 'Participant IDs must be integers.'}), 400

    if not participant_ids:
        return jsonify({'error': 'At least one participant required'}), 400

    if current_user_id not in participant_ids:
        participant_ids.append(current_user_id)

    try:
        conversation = chat_service.create_conversation(participant_ids)
    except ChatValidationError as err:
        return jsonify({'error': str(err)}), 400

    return jsonify(conversation.to_dict()), 201

@messages_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get messages for a conversation"""
    current_user_id = get_jwt_identity_int()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    try:
        messages, has_more = chat_service.get_conversation_messages(
            conversation_id,
            current_user_id,
            page=page,
            per_page=per_page,
        )
    except ChatAccessError:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'messages': [msg.to_dict() for msg in messages],
        'page': page,
        'per_page': per_page,
        'has_more': has_more,
    }), 200

@messages_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message"""
    current_user_id = get_jwt_identity_int()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    conversation_id = data.get('conversation_id')
    content = data.get('content', '').strip()
    morse_code = data.get('morse_code')
    message_type = data.get('message_type', 'text')
    input_method = data.get('input_method', 'text')

    if not conversation_id:
        return jsonify({'error': 'Conversation ID required'}), 400

    try:
        message = chat_service.create_message(
            sender_id=current_user_id,
            conversation_id=conversation_id,
            content=content,
            morse_code=morse_code,
            message_type=message_type,
            input_method=input_method,
        )
    except ChatValidationError as err:
        return jsonify({'error': str(err)}), 400
    except ChatAccessError:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(message.to_dict()), 201

@messages_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message (soft delete by clearing content)"""
    current_user_id = get_jwt_identity_int()

    try:
        chat_service.soft_delete_message(message_id, current_user_id)
    except ChatNotFoundError:
        return jsonify({'error': 'Message not found'}), 404
    except ChatAccessError:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({'message': 'Message deleted'}), 200

@messages_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by username"""
    current_user_id = get_jwt_identity_int()
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([]), 200

    users = chat_service.search_users(query, current_user_id, limit=10)
    return jsonify([user.to_dict() for user in users]), 200
