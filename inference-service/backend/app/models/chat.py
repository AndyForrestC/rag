from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: str
    content: str
    role: MessageRole
    timestamp: datetime
    session_id: str


class ChatSession(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    first_message_preview: Optional[str] = None


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    content: str
    session_id: str


class ChatSessionWithMessages(BaseModel):
    session: ChatSession
    messages: List[ChatMessage]