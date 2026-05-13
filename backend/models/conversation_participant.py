"""
Conversation participant database model for Telegraph Messenger
"""

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database.connection import Base


class ConversationParticipant(Base):
    """Conversation participant mapping"""
    __tablename__ = 'conversation_participants'
    __table_args__ = (
        UniqueConstraint('conversation_id', 'user_id', name='uq_conversation_participant'),
    )

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User", back_populates="conversations")
