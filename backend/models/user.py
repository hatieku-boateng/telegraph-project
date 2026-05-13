"""
User database model for Telegraph Messenger
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from ..database.connection import Base


class User(Base):
    """User model with authentication and profile data"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar_initials = Column(String(10))
    display_name = Column(String(100))
    bio = Column(Text, default='')
    is_online = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, index=True)
    last_login = Column(DateTime)
    email_verified = Column(Boolean, default=False)
    preferences = Column(JSON, default=dict)  # User preferences (theme, notifications, etc.)

    # Relationships
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    conversations = relationship("ConversationParticipant", back_populates="user")

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user to dictionary

        Args:
            include_sensitive: Include email and verification status

        Returns:
            Dictionary representation of user
        """
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'avatar_initials': self.avatar_initials or self.username[:2].upper(),
            'bio': self.bio or '',
            'is_online': self.is_online,
            'created_at': self.created_at.isoformat(),
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }

        if include_sensitive:
            data.update({
                'email': self.email,
                'email_verified': self.email_verified,
                'updated_at': self.updated_at.isoformat(),
                'last_login': self.last_login.isoformat() if self.last_login else None,
                'is_active': self.is_active,
            })

        return data

    def to_dict_full(self) -> dict:
        """Full user data (for admin/self only)"""
        return self.to_dict(include_sensitive=True)

    def set_online(self) -> None:
        """Mark user as online"""
        self.is_online = True
        self.last_seen = datetime.utcnow()

    def set_offline(self) -> None:
        """Mark user as offline"""
        self.is_online = False
        self.last_seen = datetime.utcnow()

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"