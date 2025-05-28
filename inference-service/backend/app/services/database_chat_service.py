"""
Database-backed chat service using SQLAlchemy and PostgreSQL
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.db_models import ChatSessionDB, ChatMessageDB


class DatabaseChatService:
    """
    Chat service with PostgreSQL persistence
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        if not title:
            title = f"New Chat {datetime.now().strftime('%m-%d %H:%M')}"
        
        session_db = ChatSessionDB(
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(session_db)
        await self.db.commit()
        await self.db.refresh(session_db)
        
        return ChatSession(
            id=str(session_db.id),
            title=session_db.title,
            created_at=session_db.created_at,
            updated_at=session_db.updated_at,
            message_count=session_db.message_count,
            first_message_preview=session_db.first_message_preview
        )

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID"""
        stmt = select(ChatSessionDB).where(ChatSessionDB.id == uuid.UUID(session_id))
        result = await self.db.execute(stmt)
        session_db = result.scalar_one_or_none()
        
        if not session_db:
            return None
        
        return ChatSession(
            id=str(session_db.id),
            title=session_db.title,
            created_at=session_db.created_at,
            updated_at=session_db.updated_at,
            message_count=session_db.message_count,
            first_message_preview=session_db.first_message_preview
        )

    async def get_session_with_messages(self, session_id: str) -> Optional[tuple[ChatSession, List[ChatMessage]]]:
        """Get a session with all its messages"""
        stmt = select(ChatSessionDB).options(
            selectinload(ChatSessionDB.messages)
        ).where(ChatSessionDB.id == uuid.UUID(session_id))
        
        result = await self.db.execute(stmt)
        session_db = result.scalar_one_or_none()
        
        if not session_db:
            return None
        
        session = ChatSession(
            id=str(session_db.id),
            title=session_db.title,
            created_at=session_db.created_at,
            updated_at=session_db.updated_at,
            message_count=session_db.message_count,
            first_message_preview=session_db.first_message_preview
        )
        
        messages = [
            ChatMessage(
                id=str(msg.id),
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp,
                session_id=str(msg.session_id)
            )
            for msg in sorted(session_db.messages, key=lambda x: x.timestamp)
        ]
        
        return session, messages

    async def list_sessions(self, limit: int = 50) -> List[ChatSession]:
        """List all sessions, ordered by update time"""
        stmt = select(ChatSessionDB).order_by(desc(ChatSessionDB.updated_at)).limit(limit)
        result = await self.db.execute(stmt)
        sessions_db = result.scalars().all()
        
        return [
            ChatSession(
                id=str(session_db.id),
                title=session_db.title,
                created_at=session_db.created_at,
                updated_at=session_db.updated_at,
                message_count=session_db.message_count,
                first_message_preview=session_db.first_message_preview
            )
            for session_db in sessions_db
        ]

    async def update_session(self, session_id: str, title: str) -> Optional[ChatSession]:
        """Update session title"""
        stmt = select(ChatSessionDB).where(ChatSessionDB.id == uuid.UUID(session_id))
        result = await self.db.execute(stmt)
        session_db = result.scalar_one_or_none()
        
        if not session_db:
            return None
        
        session_db.title = title
        session_db.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session_db)
        
        return ChatSession(
            id=str(session_db.id),
            title=session_db.title,
            created_at=session_db.created_at,
            updated_at=session_db.updated_at,
            message_count=session_db.message_count,
            first_message_preview=session_db.first_message_preview
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        stmt = select(ChatSessionDB).where(ChatSessionDB.id == uuid.UUID(session_id))
        result = await self.db.execute(stmt)
        session_db = result.scalar_one_or_none()
        
        if not session_db:
            return False
        
        await self.db.delete(session_db)
        await self.db.commit()
        return True

    async def add_message(self, session_id: str, content: str, role: MessageRole) -> ChatMessage:
        """Add a message to a session"""
        # Validate and convert session_id to UUID
        try:
            session_uuid = uuid.UUID(session_id)
        except ValueError:
            raise ValueError(f"Invalid session_id format: {session_id}")
        
        # First, get the session
        session_stmt = select(ChatSessionDB).where(ChatSessionDB.id == session_uuid)
        session_result = await self.db.execute(session_stmt)
        session_db = session_result.scalar_one_or_none()
        
        if not session_db:
            raise ValueError(f"Session {session_id} not found")
        
        # Create the message
        message_db = ChatMessageDB(
            session_id=uuid.UUID(session_id),
            content=content,
            role=role,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(message_db)
        
        # Update session stats
        session_db.message_count += 1
        session_db.updated_at = datetime.utcnow()
        
        # Update first message preview if this is the first user message
        if role == MessageRole.USER and not session_db.first_message_preview:
            preview = content[:100] + "..." if len(content) > 100 else content
            session_db.first_message_preview = preview
        
        await self.db.commit()
        await self.db.refresh(message_db)
        
        return ChatMessage(
            id=str(message_db.id),
            content=message_db.content,
            role=message_db.role,
            timestamp=message_db.timestamp,
            session_id=str(message_db.session_id)
        )

    async def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session"""
        stmt = select(ChatMessageDB).where(
            ChatMessageDB.session_id == uuid.UUID(session_id)
        ).order_by(ChatMessageDB.timestamp)
        
        result = await self.db.execute(stmt)
        messages_db = result.scalars().all()
        
        return [
            ChatMessage(
                id=str(msg.id),
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp,
                session_id=str(msg.session_id)
            )
            for msg in messages_db
        ]
