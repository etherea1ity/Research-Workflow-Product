from __future__ import annotations

from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class LLMSettings:
    use_llm: bool
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 60


class OpenAICompatibleClient:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return self.settings.use_llm and bool(self.settings.api_key and self.settings.base_url and self.settings.model)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.enabled:
            raise RuntimeError("LLM client is not enabled.")
        response = requests.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            },
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()
