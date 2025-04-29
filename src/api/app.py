"""
FastAPI application for LangManus.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import asyncio
from typing import AsyncGenerator, Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from src.graph.types import MixState

from src.graph import build_graph, mix_agents_builder
from src.config import TEAM_MEMBERS
from src.service.workflow_service import run_agent_workflow, run_mix_agent_workflow

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangManus API",
    description="API for LangManus LangGraph-based agent workflow",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the graph
graph = build_graph()
mix_graph = mix_agents_builder()


class ContentItem(BaseModel):
    type: str = Field(..., description="The type of content (text, image, etc.)")
    text: Optional[str] = Field(None, description="The text content if type is 'text'")
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="Whether to enable deep thinking mode"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="Whether to search before planning"
    )

class MixChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(False, description="Whether to enable deep thinking mode")
    search_before_planning: Optional[bool] = Field(False, description="Whether to search before planning")



@app.post("/api/chat/stream")
async def chat_endpoint(request: ChatRequest, req: Request):
    """
    Chat endpoint for LangGraph invoke.не

    Args:
        request: The chat request
        req: The FastAPI request object for connection state checking

    Returns:
        The streamed response
    """
    try:
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role}
            if isinstance(msg.content, str):
                message_dict["content"] = msg.content
            else:
                content_items = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        content_items.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_url:
                        content_items.append(
                            {"type": "image", "image_url": item.image_url}
                        )

                message_dict["content"] = content_items

            messages.append(message_dict)

        async def event_generator():
            try:
                async for event in run_agent_workflow(
                    messages,
                    request.debug,
                    request.deep_thinking_mode,
                    request.search_before_planning,
                ):
                    if await req.is_disconnected():
                        logger.info("Client disconnected, stopping workflow")
                        break
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"], ensure_ascii=False),
                    }
            except asyncio.CancelledError:
                logger.info("Stream processing cancelled")
                raise

        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            sep="\n",
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/mix/stream")
async def mix_chat_endpoint(request: MixChatRequest, req: Request):
    """
    SSE-эндоинт для микс-чат воркфлоу.
    Отправляет сначала event: answers, потом event: message чанками.
    """
    user_msgs = []
    for msg in request.messages:
        content = msg.content if isinstance(msg.content, str) else msg.content
        user_msgs.append({"role": msg.role, "content": content})

    async def event_generator():
        try:
            async for ev in run_mix_agent_workflow(
                user_input_messages=user_msgs,
                debug=request.debug,
                deep_thinking_mode=request.deep_thinking_mode,
                search_before_planning=request.search_before_planning,
            ):
                # Если клиент прервал соединение — останавливаемся
                if await req.is_disconnected():
                    logger.info("Client disconnected, stopping stream")
                    break

                # Иначе пересылаем клиенту
                yield {
                    "event": ev["event"],
                    "data": ev["data"],
                }

        except asyncio.CancelledError:
            logger.info("Stream cancelled by client")
        except Exception as e:
            logger.exception("Error in mix_chat_endpoint")
            # В случае ошибки шлем клиенту сообщение об ошибке и завершаем стрим
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }

    # Возвращаем SSE-ответ. sep="\n" даёт нормальные разделители
    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        sep="\n",
    )