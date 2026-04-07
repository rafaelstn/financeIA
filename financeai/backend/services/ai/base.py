from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, message: str, history: list[dict], system_prompt: str
    ) -> str:
        ...
