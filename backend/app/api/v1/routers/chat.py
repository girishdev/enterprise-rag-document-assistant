from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user

# Normal /chat endpoint still uses Mock for now
from app.llm.mock_provider import MockLLMProvider

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message

from app.schemas.chat import ChatRequest, ChatResponse

from app.services.chat_service import ChatService
from app.services.rag_service import RAGService

from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.repositories.message_repository import (
    MessageRepository,
)
import json


router = APIRouter()


# ---------------------------------------------------------
# Normal Chat API
# ---------------------------------------------------------

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = ChatService(
        db=db,
        llm_provider=MockLLMProvider(),
    )

    try:
        conversation, reply = await service.chat(
            user_id=current_user.id,
            message_text=request.message,
            conversation_id=request.conversation_id,
        )

    except ValueError as exc:

        if str(exc) == "CONVERSATION_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        if str(exc) == "FORBIDDEN":
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

        raise

    return ChatResponse(
        conversation_id=conversation.id,
        reply=reply,
    )


# ---------------------------------------------------------
# RAG Streaming Chat API
# ---------------------------------------------------------

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    conversation_repository = ConversationRepository(db)
    message_repository = MessageRepository(db)

    # -----------------------------------------------------
    # 1. Create or load conversation
    # -----------------------------------------------------

    if request.conversation_id is None:

        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:80],
        )

        conversation = conversation_repository.create(
            conversation
        )

    else:

        conversation = conversation_repository.get_by_id(
            request.conversation_id
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

    # -----------------------------------------------------
    # 2. Save user message
    # -----------------------------------------------------

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    message_repository.create(
        user_message
    )

    # -----------------------------------------------------
    # 3. Generate real RAG response
    # -----------------------------------------------------

    rag_service = RAGService(db)

    rag_result = await rag_service.answer(
        question=request.message,
        owner_id=current_user.id,
        document_id=request.document_id,
    )

    reply = rag_result["answer"]
    sources = rag_result["sources"]

    # -----------------------------------------------------
    # 4. Save assistant response
    # -----------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
    )

    message_repository.create(
        assistant_message
    )

    # -----------------------------------------------------
    # 5. Send response to React using SSE
    # -----------------------------------------------------

    async def event_generator():

        safe_reply = reply.replace("\n", " ")

        yield f"data: {safe_reply}\n\n"

        yield (
            f"data: [SOURCES:{json.dumps(sources)}]\n\n"
        )

        yield (
            f"data: [DONE:{conversation.id}]\n\n"
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )