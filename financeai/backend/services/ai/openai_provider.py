import json
from typing import Callable

from openai import OpenAI
from services.ai.base import AIProvider
from config import settings


class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    def _format_tools(self, tools: list[dict]) -> list[dict]:
        """Convert generic tool definitions to OpenAI function-calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
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
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        openai_tools = self._format_tools(tools) if tools else None

        # Tool-calling loop: max 5 iterations
        for _ in range(5):
            kwargs = {"model": self.model, "messages": messages}
            if openai_tools:
                kwargs["tools"] = openai_tools

            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            # If no tool calls, return the text content
            if not choice.message.tool_calls:
                return choice.message.content or ""

            # If we have no executor, just return whatever text we got
            if not tool_executor:
                return choice.message.content or ""

            # Add assistant message with tool calls to conversation
            messages.append(choice.message)

            # Execute each tool call and add results
            for tool_call in choice.message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                result = tool_executor(func_name, func_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        # Fallback: if loop exhausted, do one final call without tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
