"""Thin, provider-agnostic wrapper around whichever LLM backend is configured.

Every agent calls through this one class. Swapping models or providers,
or adding retry/rate-limit handling, happens here -- never inside an
agent, and never inside the orchestrator.
"""
from __future__ import annotations

import json
import os

import anthropic


class LLMClient:
    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        self.model = model
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    async def complete_json(self, system: str, user: str, max_tokens: int = 2000) -> list[dict]:
        """Send a prompt and parse a JSON array out of the response.

        Centralizing parsing here means every agent gets the same
        tolerance for stray markdown fences, and any future retry logic
        only needs to be written once.
        """
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()

        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text.split("\n", 1)[-1]

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return []

        return parsed if isinstance(parsed, list) else []
