import asyncio

from app.llm.base import LLMProvider


class MockStreamLLMProvider(LLMProvider):

    async def generate(
        self,
        messages: list[dict],
    ) -> str:
        return "Mock response"

    async def stream(
        self,
        messages: list[dict],
    ):
        response = (
            "This is a mock streaming AI response."
        )

        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.1)