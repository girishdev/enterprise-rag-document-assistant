from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):

    async def generate(
        self,
        messages: list[dict],
    ) -> str:

        last_user_message = next(
            (
                message["content"]
                for message in reversed(messages)
                if message["role"] == "user"
            ),
            "",
        )

        return (
            "Mock AI Response: "
            f"You asked: {last_user_message}"
        )