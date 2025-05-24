from typing import List
import json
import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from llama_index.core.llms import MessageRole
from pydantic import BaseModel
from nemoguardrails import LLMRails, RailsConfig

from app.config.actions import init, init_streaming, get_streaming_query_response

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(data: _ChatData):
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

    # Load a guardrails configuration from the specified path.
    config = RailsConfig.from_path("./app/config")
    rails = LLMRails(config)

    # call generate_async
    response = await rails.generate_async(prompt=lastMessage.content)

    return response


@r.post("/stream")
async def chat_stream(data: _ChatData):
    """
    Streaming chat endpoint that provides real-time response streaming
    """
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

    # Get the streaming query engine
    query_engine = init_streaming()

    async def generate_stream():
        try:
            # Use streaming query method
            streaming_response = get_streaming_query_response(query_engine, lastMessage.content)

            # Check if response has streaming capability
            if hasattr(streaming_response, 'response_gen') and streaming_response.response_gen:
                # Stream each token directly as text
                for token in streaming_response.response_gen:
                    if token:
                        yield token
                        await asyncio.sleep(0.01)  # Small delay for better UX
            else:
                # Fallback: send complete response
                response_text = str(streaming_response)
                yield response_text

        except Exception as e:
            yield f"Error: {str(e)}"

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
