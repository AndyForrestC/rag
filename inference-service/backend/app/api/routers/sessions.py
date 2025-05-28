from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import (
    ChatSession, 
    ChatSessionWithMessages, 
    CreateSessionRequest, 
    UpdateSessionRequest
)
from app.database import get_database
from app.services.database_chat_service import DatabaseChatService

sessions_router = r = APIRouter()


@r.post("", response_model=ChatSession)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_database)
):
    """Create a new chat session"""
    service = DatabaseChatService(db)
    return await service.create_session(request.title)


@r.get("", response_model=List[ChatSession])
async def get_sessions(db: AsyncSession = Depends(get_database)):
    """Get all chat sessions"""
    service = DatabaseChatService(db)
    return await service.list_sessions()


@r.get("/{session_id}", response_model=ChatSessionWithMessages)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get a specific session and its messages"""
    service = DatabaseChatService(db)
    result = await service.get_session_with_messages(session_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session, messages = result
    return ChatSessionWithMessages(session=session, messages=messages)


@r.put("/{session_id}", response_model=ChatSession)
async def update_session(
    session_id: str, 
    request: UpdateSessionRequest,
    db: AsyncSession = Depends(get_database)
):
    """Update session title"""
    service = DatabaseChatService(db)
    session = await service.update_session(session_id, request.title)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@r.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete a session"""
    service = DatabaseChatService(db)
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session deleted successfully"}
