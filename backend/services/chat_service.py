"""
Chat service for message and conversation business logic
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from ..database.connection import get_db
from ..models import User, Message, Conversation, ConversationParticipant


class ChatServiceError(Exception):
    """Base exception for chat service errors."""


class ChatValidationError(ChatServiceError):
    """Validation failed for chat service operations."""


class ChatNotFoundError(ChatServiceError):
    """Requested chat object was not found."""


class ChatAccessError(ChatServiceError):
    """Access to the requested chat resource was denied."""


class ChatService:
    """Service class for chat-related operations."""

    def _has_participation(self, conversation_id: int, user_id: int) -> bool:
        db = get_db()
        return db.query(ConversationParticipant.id).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id
        ).first() is not None

    def create_conversation(self, participant_ids: List[int], name: Optional[str] = None) -> Conversation:
        """Create a new conversation and participant membership."""
        if not participant_ids:
            raise ChatValidationError('At least one participant is required.')

        try:
            participant_ids = [int(pid) for pid in participant_ids]
        except (TypeError, ValueError):
            raise ChatValidationError('Participant IDs must be integers.')

        unique_participant_ids = list(dict.fromkeys(participant_ids))
        db = get_db()
        valid_ids = {
            user_id for (user_id,) in db.query(User.id).filter(User.id.in_(unique_participant_ids)).all()
        }

        if len(valid_ids) != len(unique_participant_ids):
            raise ChatValidationError('One or more participants were not found.')

        conversation = Conversation(name=name)
        db.add(conversation)
        db.flush()

        db.add_all([
            ConversationParticipant(conversation_id=conversation.id, user_id=user_id)
            for user_id in unique_participant_ids
        ])

        db.commit()
        db.refresh(conversation)
        return conversation

    def create_message(
        self,
        sender_id: int,
        conversation_id: int,
        content: Optional[str] = None,
        morse_code: Optional[str] = None,
        message_type: str = 'text',
        input_method: str = 'text',
    ) -> Message:
        """Create a new message in an existing conversation."""
        if not content and not morse_code:
            raise ChatValidationError('Message content or Morse code is required.')

        if not self._has_participation(conversation_id, sender_id):
            raise ChatAccessError('Access denied.')

        db = get_db()
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            morse_code=morse_code,
            message_type=message_type,
            input_method=input_method,
        )

        db.add(message)
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message

    def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
        page: int = 1,
        per_page: int = 50,
    ) -> Tuple[List[Message], bool]:
        """Return paginated messages for a conversation."""
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10

        if not self._has_participation(conversation_id, user_id):
            raise ChatAccessError('Access denied.')

        db = get_db()
        offset = (page - 1) * per_page
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).offset(offset).limit(per_page + 1).all()

        has_more = len(messages) > per_page
        return list(reversed(messages[:per_page])), has_more

    def soft_delete_message(self, message_id: int, user_id: int) -> None:
        """Soft delete a message if the sender has permission."""
        db = get_db()
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ChatNotFoundError('Message not found.')

        if message.sender_id != user_id:
            raise ChatAccessError('Access denied.')

        message.content = '[Message deleted]'
        message.morse_code = None
        db.commit()

    def mark_messages_read(self, conversation_id: int, user_id: int) -> None:
        """Mark pending messages as read for a participant."""
        if not self._has_participation(conversation_id, user_id):
            raise ChatAccessError('Access denied.')

        db = get_db()
        db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False,
        ).update({'is_read': True})
        db.commit()

    def get_user_conversations(self, user_id: int, page: int = 1, per_page: int = 50) -> List[Conversation]:
        """Return the current user's conversations ordered by activity."""
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10

        db = get_db()
        offset = (page - 1) * per_page

        return db.query(Conversation).join(ConversationParticipant).filter(
            ConversationParticipant.user_id == user_id
        ).order_by(desc(Conversation.updated_at), desc(Conversation.created_at)).options(
            joinedload(Conversation.participants).joinedload(ConversationParticipant.user)
        ).offset(offset).limit(per_page).all()

    def search_users(self, query: str, current_user_id: int, limit: int = 10) -> List[User]:
        """Search users by username while excluding the current user."""
        db = get_db()
        return db.query(User).filter(
            User.username.ilike(f'%{query}%'),
            User.id != current_user_id,
        ).limit(limit).all()

    def update_user_presence(self, user_id: int, is_online: bool) -> None:
        """Update user's online availability and last seen timestamp."""
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_online = is_online
            if not is_online:
                user.last_seen = datetime.utcnow()
            db.commit()

    def get_online_users(self) -> List[User]:
        """Return all currently online users."""
        db = get_db()
        return db.query(User).filter(User.is_online == True).all()


chat_service = ChatService()
