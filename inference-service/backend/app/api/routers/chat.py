from typing import List, Optional
import asyncio
import logging

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from llama_index.core.llms import MessageRole
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.actions import init_streaming, get_streaming_query_response
from app.database import get_database
from app.services.database_chat_service import DatabaseChatService
from app.services.guardrails_service import get_guardrails_service
from app.models.chat import MessageRole as ChatMessageRole

logger = logging.getLogger(__name__)

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]
    session_id: Optional[str] = None


@r.post("")
async def chat(data: _ChatData, db: AsyncSession = Depends(get_database)):
    """
    Enhanced chat endpoint with streaming support, session persistence, and safety guardrails
    """
    logger.info(f"Received chat data: {data}")
    logger.info(f"Messages: {data.messages}")
    logger.info(f"Session ID: {data.session_id}")
    
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )

    # Initialize guardrails service
    guardrails = get_guardrails_service()
    
    # Check input safety with guardrails
    input_check = await guardrails.check_input(lastMessage.content)
    if not input_check["allowed"]:
        logger.warning(f"Input blocked by guardrails: {input_check['reason']}")
        # Return a safe response immediately
        safe_response = "I'm sorry, I can't respond to that request. Please try asking something else."
        
        # Still handle session management for blocked requests
        db_service = DatabaseChatService(db)
        current_session_id = data.session_id
        
        if not current_session_id:
            title = lastMessage.content[:50] + "..." if len(lastMessage.content) > 50 else lastMessage.content
            new_session = await db_service.create_session(title)
            current_session_id = new_session.id
        
        try:
            await db_service.add_message(current_session_id, lastMessage.content, ChatMessageRole.USER)
            await db_service.add_message(current_session_id, safe_response, ChatMessageRole.ASSISTANT)
        except ValueError as e:
            if "Invalid session_id format" in str(e) or "Session" in str(e) and "not found" in str(e):
                title = lastMessage.content[:50] + "..." if len(lastMessage.content) > 50 else lastMessage.content
                new_session = await db_service.create_session(title)
                current_session_id = new_session.id
                await db_service.add_message(current_session_id, lastMessage.content, ChatMessageRole.USER)
                await db_service.add_message(current_session_id, safe_response, ChatMessageRole.ASSISTANT)
        
        async def blocked_response():
            yield safe_response
        
        return StreamingResponse(
            blocked_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )
    
    # Use the potentially modified input from guardrails
    user_message_content = input_check.get("modified_input", lastMessage.content)

    # Handle session management
    db_service = DatabaseChatService(db)
    current_session_id = data.session_id
    
    # If no session_id provided or invalid, create a new session
    if not current_session_id:
        # Create a new session with the user's message as title (first 50 chars)
        title = user_message_content[:50] + "..." if len(user_message_content) > 50 else user_message_content
        new_session = await db_service.create_session(title)
        current_session_id = new_session.id
    
    # Save user message to session
    try:
        await db_service.add_message(current_session_id, user_message_content, ChatMessageRole.USER)
    except ValueError as e:
        # If session_id is invalid, create a new session
        if "Invalid session_id format" in str(e) or "Session" in str(e) and "not found" in str(e):
            title = user_message_content[:50] + "..." if len(user_message_content) > 50 else user_message_content
            new_session = await db_service.create_session(title)
            current_session_id = new_session.id
            await db_service.add_message(current_session_id, user_message_content, ChatMessageRole.USER)
        else:
            raise e

    # Get the streaming query engine
    query_engine = init_streaming()

    async def generate_stream():
        try:
            # Use streaming query method with the checked input
            streaming_response = get_streaming_query_response(query_engine, user_message_content)
            
            full_response = ""
            # Check if response has streaming capability
            if hasattr(streaming_response, 'response_gen') and streaming_response.response_gen:
                # Stream each token and apply output checking
                for token in streaming_response.response_gen:
                    if token:
                        full_response += token
                        yield token
                        await asyncio.sleep(0.01)  # Small delay for better UX
            else:
                # Fallback: send complete response
                response_text = str(streaming_response)
                full_response = response_text
                yield response_text
            
            # Apply output safety check before saving to database
            if full_response:
                output_check = await guardrails.check_output(full_response, user_message_content)
                
                # Use the potentially modified output from guardrails
                final_response = output_check.get("modified_output", full_response)
                
                if not output_check["allowed"]:
                    logger.warning(f"Output modified by guardrails: {output_check['reason']}")
                    # If output was blocked, send a safe replacement
                    safe_replacement = "I apologize, but I cannot provide that response due to safety guidelines. Please try rephrasing your question."
                    yield safe_replacement
                    final_response = safe_replacement
                
                # Save final (potentially modified) response to session
                await db_service.add_message(current_session_id, final_response, ChatMessageRole.ASSISTANT)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield error_message
            # Save error message to session
            if current_session_id:
                await db_service.add_message(current_session_id, error_message, ChatMessageRole.ASSISTANT)

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )



