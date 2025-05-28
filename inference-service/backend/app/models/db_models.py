"""
SQLAlchemy models for chat sessions and messages
"""
from datetime import datetime
from typing import List
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.database import Base
from app.models.chat import MessageRole


class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
    first_message_preview = Column(Text, nullable=True)

    # Relationship to messages
    messages = relationship("ChatMessageDB", back_populates="session", cascade="all, delete-orphan")


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSONB, nullable=True)  # For additional data like model parameters

    # Relationship to session
    session = relationship("ChatSessionDB", back_populates="messages")
