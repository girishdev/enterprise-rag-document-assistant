import asyncio

from app.llm.ollama_provider import OllamaLLMProvider


async def main():
    provider = OllamaLLMProvider()

    response = await provider.generate([
        {
            "role": "user",
            "content": "Explain RAG in one sentence.",
        }
    ])

    print(response)


asyncio.run(main())