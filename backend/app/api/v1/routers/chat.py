from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
# from app.llm.openai_provider import OpenAIProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.mock_stream_provider import MockStreamLLMProvider
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


router = APIRouter()


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
        # llm_provider=OpenAIProvider(),
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

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    message_repository.create(user_message)

    messages = message_repository.list_by_conversation(
        conversation.id
    )

    llm_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    provider = MockStreamLLMProvider()

    async def event_generator():
        full_response = ""

        async for chunk in provider.stream(llm_messages):
            full_response += chunk

            yield f"data: {chunk}\n\n"

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response.strip(),
        )

        message_repository.create(
            assistant_message
        )

        yield (
            f"data: [DONE:{conversation.id}]\n\n"
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )