from abc import ABC, abstractmethod
from typing import Callable


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Generate a response from the AI provider.

        If tools and tool_executor are provided, the provider handles
        the tool-calling loop internally and returns the final text response.

        Args:
            message: The user's message.
            history: Conversation history as list of {"role": ..., "content": ...}.
            system_prompt: System prompt with context.
            tools: Tool definitions in a provider-agnostic format.
            tool_executor: Callable(name, args) -> str that executes a tool.

        Returns:
            The final text response from the AI.
        """
        ...
