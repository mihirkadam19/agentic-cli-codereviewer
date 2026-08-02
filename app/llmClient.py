"""Thin, provider-agnostic wrapper around whichever LLM backend is configured.

Every agent calls through this one class. Swapping models or providers,
or adding retry/rate-limit handling, happens here -- never inside an
agent, and never inside the orchestrator.
"""
from __future__ import annotations

import os

import anthropic

REPORT_FINDINGS_TOOL = {
    "name": "report_findings",
    "description": "Report code review findings as structured data. Call this even if there are zero findings -- pass an empty list.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "file": {"type": "string", "description": "Path of the file this finding applies to"},
                        "line": {"type": ["integer", "null"], "description": "Line number, or null if not line-specific"},
                        "severity": {"type": "string", "enum": ["info", "warning", "error"]},
                        "message": {"type": "string", "description": "What the issue is"},
                        "suggestion": {"type": ["string", "null"], "description": "How to fix it, or null"},
                    },
                    "required": ["file", "severity", "message"],
                },
            }
        },
        "required": ["findings"],
    },
}


class LLMClient:
    def __init__(self, model: str = "claude-sonnet-4-6", api_key: str | None = None):
        self.model = model
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    async def complete_findings(self, system: str, user: str, max_tokens: int = 2000) -> list[dict]:
        """Send a prompt and get back structured findings via a forced tool call.

        No JSON parsing, no markdown-fence stripping, no silent [] fallback
        on a malformed response -- the API validates the shape before it
        ever reaches this code.
        """
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            tools=[REPORT_FINDINGS_TOOL],
            tool_choice={"type": "tool", "name": "report_findings"},
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "report_findings":
                return block.input.get("findings", [])

        return []