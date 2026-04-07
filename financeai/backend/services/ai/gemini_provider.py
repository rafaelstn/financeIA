from google import genai
from services.ai.base import AIProvider
from config import settings


class GeminiProvider(AIProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash"

    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        contents = []
        # Add history
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        # Add current message
        contents.append({"role": "user", "parts": [{"text": message}]})

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={"system_instruction": system_prompt},
        )
        return response.text
