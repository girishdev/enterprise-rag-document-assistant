from openai import AsyncOpenAI

from app.embeddings.base import EmbeddingProvider
from app.core.config import settings


class OpenAIEmbeddingProvider(EmbeddingProvider):

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

    async def embed(self, text: str) -> list[float]:

        response = await self.client.embeddings.create(
            model="text-embedding-3-small", # gives us: 1536 dimensions, which matches: Vector(1536)
            input=text,
        )

        return response.data[0].embedding