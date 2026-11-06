import httpx

from app.llm.base import LLMProvider


class OllamaLLMProvider(LLMProvider):

    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.model = "llama3.2:3b"

    async def generate(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
            )

            response.raise_for_status()

            data = response.json()

            return data["message"]["content"]