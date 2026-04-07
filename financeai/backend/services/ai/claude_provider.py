import json
from typing import Callable

import anthropic
from services.ai.base import AIProvider
from config import settings


class ClaudeProvider(AIProvider):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def _format_tools(self, tools: list[dict]) -> list[dict]:
        """Convert generic tool definitions to Claude tool format."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"],
            }
            for t in tools
        ]

    async def generate_response(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        messages = []
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        claude_tools = self._format_tools(tools) if tools else None

        # Tool-calling loop: max 5 iterations
        for _ in range(5):
            kwargs = {
                "model": self.model,
                "max_tokens": 2048,
                "system": system_prompt,
                "messages": messages,
            }
            if claude_tools:
                kwargs["tools"] = claude_tools

            response = self.client.messages.create(**kwargs)

            # Separate text and tool_use blocks
            text_parts = []
            tool_uses = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if not tool_uses or response.stop_reason != "tool_use":
                return "\n".join(text_parts) if text_parts else ""

            if not tool_executor:
                return "\n".join(text_parts) if text_parts else ""

            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute tools and add results
            tool_results = []
            for tu in tool_uses:
                result_str = tool_executor(tu.name, tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result_str,
                })

            messages.append({"role": "user", "content": tool_results})

        # Fallback: final call without tools
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )
        text_parts = [b.text for b in response.content if b.type == "text"]
        return "\n".join(text_parts) if text_parts else ""
