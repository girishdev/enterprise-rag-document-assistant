from app.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.llm.ollama_provider import OllamaLLMProvider
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.retrieval_service import RetrievalService
from uuid import UUID


class RAGService:

    def __init__(self, db):
        chunk_repository = DocumentChunkRepository(db)

        self.retrieval_service = RetrievalService(
            chunk_repository=chunk_repository,
            embedding_provider=OllamaEmbeddingProvider(),
        )

        self.llm_provider = OllamaLLMProvider()

    async def answer(
            self,
            question: str,
            owner_id: UUID,
    ) -> dict:

        chunks = await self.retrieval_service.search(
            query=question,
            owner_id=owner_id,
            limit=5,
        )

        if not chunks:
            return {
                "answer": (
                    "I could not find the answer "
                    "in the uploaded documents."
                ),
                "sources": [],
            }

        context = "\n\n".join(
            chunk.content
            for chunk in chunks
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question only using "
                    "the provided document context. "
                    "If the answer is not present in the context, "
                    "say: I could not find the answer in the documents."
                ),
            },
            {
                "role": "user",
                "content": f"""
Document context:

{context}

Question:
{question}
""",
            },
        ]

        answer = await self.llm_provider.generate(messages)

        sources = [
            {
                "document_id": str(chunk.document_id),
                "filename": chunk.document.original_filename,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }