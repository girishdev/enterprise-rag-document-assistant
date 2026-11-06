from uuid import UUID

from app.embeddings.base import EmbeddingProvider
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)


class EmbeddingService:

    def __init__(
        self,
        chunk_repository: DocumentChunkRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.chunk_repository = chunk_repository
        self.embedding_provider = embedding_provider

    async def embed_document(
        self,
        document_id: UUID,
    ) -> None:

        chunks = self.chunk_repository.list_by_document(
            document_id
        )

        for chunk in chunks:

            embedding = await self.embedding_provider.embed(
                chunk.content
            )

            self.chunk_repository.update_embedding(
                chunk,
                embedding,
            )