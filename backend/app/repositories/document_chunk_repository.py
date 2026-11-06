from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        self.db.add_all(chunks)
        self.db.commit()

        return chunks

    def list_by_document(
        self,
        document_id: UUID,
    ) -> list[DocumentChunk]:

        statement = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id
                == document_id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def delete_by_document(
        self,
        document_id: UUID,
    ) -> None:

        statement = delete(
            DocumentChunk
        ).where(
            DocumentChunk.document_id
            == document_id
        )

        self.db.execute(statement)
        self.db.commit()

    def update_embedding(
            self,
            chunk: DocumentChunk,
            embedding: list[float],
    ) -> DocumentChunk:
        chunk.embedding = embedding

        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def search_similar(
            self,
            query_embedding: list[float],
            owner_id: UUID,
            limit: int = 5,
            max_distance: float = 0.6,
    ) -> list[DocumentChunk]:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        statement = (
            select(DocumentChunk)
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                DocumentChunk.embedding.is_not(None),
                Document.owner_id == owner_id,
                distance <= max_distance,
            )
            .order_by(distance)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )