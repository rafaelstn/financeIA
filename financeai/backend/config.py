from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    def validate(self):
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL not set")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY not set")
        provider = self.AI_PROVIDER.lower()
        if provider == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set for gemini provider")
        if provider == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set for openai provider")
        if provider == "claude" and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set for claude provider")


settings = Settings()
settings.validate()
