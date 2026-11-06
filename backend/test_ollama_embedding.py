import asyncio

from app.embeddings.ollama_provider import OllamaEmbeddingProvider


async def main():
    provider = OllamaEmbeddingProvider()

    embedding = await provider.embed(
        "What is the warranty period?"
    )

    print("Embedding dimension:", len(embedding))
    print("First 5 values:", embedding[:5])


asyncio.run(main())