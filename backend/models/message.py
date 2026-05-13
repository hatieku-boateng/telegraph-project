"""
Message database model for Telegraph Messenger
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from ..database.connection import Base


class Message(Base):
    """Message model"""
    __tablename__ = 'messages'
    __table_args__ = (
        Index('ix_messages_conversation_created_at', 'conversation_id', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(Text)
    morse_code = Column(Text)
    message_type = Column(String(20), default='text')
    input_method = Column(String(20), default='keyboard')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_read = Column(Boolean, default=False, index=True)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    morse_signals = relationship("MorseSignal", back_populates="message", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender': self.sender.to_dict(),
            'content': self.content,
            'morse_code': self.morse_code,
            'message_type': self.message_type,
            'input_method': self.input_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read
        }
