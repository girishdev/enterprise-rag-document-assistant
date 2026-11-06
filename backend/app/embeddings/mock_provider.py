import hashlib

from app.embeddings.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):

    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()

        values = []

        while len(values) < 1536:
            for byte in digest:
                values.append(byte / 255.0)

                if len(values) == 1536:
                    break

        return values