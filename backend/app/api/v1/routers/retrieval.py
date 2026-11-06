from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


@router.get("/search")
async def search_chunks(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    repository = DocumentChunkRepository(db)

    service = RetrievalService(
        chunk_repository=repository,
        embedding_provider=MockEmbeddingProvider(),
    )

    chunks = await service.search(
        query=query,
        limit=limit,
    )

    return [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
        }
        for chunk in chunks
    ]