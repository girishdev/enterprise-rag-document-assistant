from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationRead
from app.schemas.message import MessageRead


router = APIRouter()


@router.get(
    "",
    response_model=list[ConversationRead],
)
def list_conversations(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    repository = ConversationRepository(db)

    return repository.list_by_user(
        current_user.id
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageRead],
)
def list_messages(
    conversation_id: UUID,
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

    conversation = conversation_repository.get_by_id(
        conversation_id
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

    message_repository = MessageRepository(db)

    return message_repository.list_by_conversation(
        conversation_id
    )