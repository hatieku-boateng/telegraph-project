"""
Morse signal database model for Telegraph Messenger
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from ..database.connection import Base


class MorseSignal(Base):
    """Morse signal data for analysis"""
    __tablename__ = 'morse_signals'
    __table_args__ = (
        Index('ix_morse_signals_message_id', 'message_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey('messages.id', ondelete='CASCADE'), nullable=False, index=True)
    signal_sequence = Column(Text)
    audio_features = Column(JSON)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="morse_signals")

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'signal_sequence': self.signal_sequence,
            'audio_features': self.audio_features,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
