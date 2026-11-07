from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    document_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str