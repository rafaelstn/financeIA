from services.ai.base import AIProvider
from config import settings


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        from services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider == "claude":
        from services.ai.claude_provider import ClaudeProvider
        return ClaudeProvider()
    elif provider == "openai":
        from services.ai.openai_provider import OpenAIProvider
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}. Use 'gemini', 'claude', or 'openai'.")
