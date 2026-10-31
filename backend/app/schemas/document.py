from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: UUID
    owner_id: UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    processing_status: str
    page_count: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)