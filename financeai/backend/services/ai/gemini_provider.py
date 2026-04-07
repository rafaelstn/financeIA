import json
from typing import Callable

from google import genai
from google.genai import types
from services.ai.base import AIProvider
from config import settings


class GeminiProvider(AIProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash"

    def _format_tools(self, tools: list[dict]) -> list[types.Tool]:
        """Convert generic tool definitions to Gemini function declarations."""
        declarations = []
        for t in tools:
            declarations.append(types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"],
            ))
        return [types.Tool(function_declarations=declarations)]

    async def generate_response(
        self,
        message: str,
        history: list[dict],
        system_prompt: str,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        gemini_tools = self._format_tools(tools) if tools else None

        config = {"system_instruction": system_prompt}

        # Tool-calling loop: max 5 iterations
        for _ in range(5):
            kwargs = {
                "model": self.model,
                "contents": contents,
                "config": config,
            }
            if gemini_tools:
                kwargs["config"] = {**config, "tools": gemini_tools}

            response = self.client.models.generate_content(**kwargs)

            # Check for function calls in the response
            function_calls = []
            text_parts = []
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_calls.append(part.function_call)
                    elif part.text:
                        text_parts.append(part.text)

            if not function_calls:
                return response.text or ""

            if not tool_executor:
                return "\n".join(text_parts) if text_parts else ""

            # Add model response to contents
            contents.append(response.candidates[0].content)

            # Execute function calls and add results
            function_responses = []
            for fc in function_calls:
                func_args = dict(fc.args) if fc.args else {}
                result_str = tool_executor(fc.name, func_args)
                result_data = json.loads(result_str)
                function_responses.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response=result_data,
                    )
                )

            contents.append({"role": "user", "parts": function_responses})

        # Fallback
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={"system_instruction": system_prompt},
        )
        return response.text or ""
