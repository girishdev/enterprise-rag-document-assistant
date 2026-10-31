from openai import AsyncOpenAI

from app.core.config import get_settings
from app.llm.base import LLMProvider


settings = get_settings()


class OpenAIProvider(LLMProvider):

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

    async def generate(
        self,
        messages: list[dict],
    ) -> str:

        response = await self.client.responses.create(
            model=settings.openai_model,
            instructions=settings.chat_system_prompt,
            input=messages,
            max_output_tokens=settings.chat_max_output_tokens,
        )

        return response.output_text