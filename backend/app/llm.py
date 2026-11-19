from abc import ABC, abstractmethod

import httpx

from backend.app.config import Settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str: ...


class OllamaQwenProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.settings.ollama_base_url}/api/generate", json={
                    "model": self.settings.llm_model, "prompt": prompt, "stream": False,
                    "options": {"temperature": 0.1},
                })
                response.raise_for_status()
                return response.json()["response"]
        except (httpx.HTTPError, KeyError):
            return "Local Qwen is unavailable. The evidence below remains available for review."


def get_llm(settings: Settings) -> LLMProvider:
    if settings.llm_provider != "ollama":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    return OllamaQwenProvider(settings)
