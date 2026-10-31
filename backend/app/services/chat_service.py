from uuid import UUID

from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


class ChatService:

    def __init__(
        self,
        db: Session,
        llm_provider: LLMProvider,
    ):
        self.db = db
        self.llm_provider = llm_provider

        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)

    async def chat(
        self,
        user_id: UUID,
        message_text: str,
        conversation_id: UUID | None = None,
    ) -> tuple[Conversation, str]:

        if conversation_id is None:
            conversation = Conversation(
                user_id=user_id,
                title=message_text[:80],
            )

            conversation = self.conversation_repository.create(
                conversation
            )

        else:
            conversation = self.conversation_repository.get_by_id(
                conversation_id
            )

            if conversation is None:
                raise ValueError("CONVERSATION_NOT_FOUND")

            if conversation.user_id != user_id:
                raise ValueError("FORBIDDEN")

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=message_text,
        )

        self.message_repository.create(
            user_message
        )

        previous_messages = (
            self.message_repository.list_by_conversation(
                conversation.id
            )
        )

        llm_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in previous_messages
        ]

        reply = await self.llm_provider.generate(
            llm_messages
        )

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply,
        )

        self.message_repository.create(
            assistant_message
        )

        return conversation, reply