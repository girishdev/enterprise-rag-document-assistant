from app.embeddings.base import EmbeddingProvider
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from uuid import UUID
from app.services.reranking_service import RerankingService


class RetrievalService:

    def __init__(
        self,
        chunk_repository: DocumentChunkRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.chunk_repository = chunk_repository
        self.embedding_provider = embedding_provider
        self.reranking_service = RerankingService()

    async def search(
            self,
            query: str,
            owner_id: UUID,
            limit: int = 5,
            document_id: UUID | None = None,
    ):

        query_embedding = await self.embedding_provider.embed(
            query
        )

        vector_results = self.chunk_repository.search_similar(
            query_embedding=query_embedding,
            owner_id=owner_id,
            limit=limit,
            document_id=document_id,
        )

        keyword_results = self.chunk_repository.search_keyword(
            query=query,
            owner_id=owner_id,
            limit=limit,
            document_id=document_id,
        )

        combined = []

        seen_ids = set()

        for chunk in vector_results + keyword_results:
            if chunk.id not in seen_ids:
                combined.append(chunk)
                seen_ids.add(chunk.id)

        return self.reranking_service.rerank(
            query=query,
            chunks=combined,
            limit=limit,
        )