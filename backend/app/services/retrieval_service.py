from app.embeddings.base import EmbeddingProvider
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from uuid import UUID


class RetrievalService:

    def __init__(
        self,
        chunk_repository: DocumentChunkRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.chunk_repository = chunk_repository
        self.embedding_provider = embedding_provider

    async def search(
            self,
            query: str,
            owner_id: UUID,
            limit: int = 5,
    ):
        query_embedding = await self.embedding_provider.embed(
            query
        )

        return self.chunk_repository.search_similar(
            query_embedding=query_embedding,
            owner_id=owner_id,
            limit=limit,
        )