import httpx

from app.embeddings.base import EmbeddingProvider


class OllamaEmbeddingProvider(EmbeddingProvider):

    def __init__(self):
        self.url = "http://localhost:11434/api/embed"
        self.model = "nomic-embed-text"

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json={
                    "model": self.model,
                    "input": text,
                },
            )

            response.raise_for_status()

            data = response.json()

            return data["embeddings"][0]