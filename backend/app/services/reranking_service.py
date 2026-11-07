from sentence_transformers import CrossEncoder


class RerankingService:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query: str,
        chunks: list,
        limit: int = 5,
    ) -> list:

        if not chunks:
            return []

        pairs = [
            [query, chunk.content]
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            chunk
            for chunk, _ in ranked[:limit]
        ]