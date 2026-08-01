"""Abstract base for all review agents. Defines shared behavior
(LLM call flow, JSON parsing, Finding construction) but leaves
SYSTEM_PROMPT for subclasses to supply."""

from __future__ import annotations

from app.llmClient import LLMClient
from app.schema import Context, Diff, Finding, Severity


class BaseAgent:
    name: str = "base"
    SYSTEM_PROMPT: str = ""

    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def review(self, diff: Diff, context: Context) -> list[Finding]:
        prompt = self._build_prompt(diff, context)
        raw_findings = await self._llm.complete_json(self.SYSTEM_PROMPT, prompt)
        return [self._to_finding(item) for item in raw_findings if "message" in item]

    def _build_prompt(self, diff: Diff, context: Context) -> str:
        parts = []
        for f in diff.files:
            parts.append(f"--- {f.path} ---\n{f.hunk}")
            if f.path in context.snippets:
                parts.append(f"[context]\n{context.snippets[f.path]}")
        return "\n\n".join(parts)

    def _to_finding(self, item: dict) -> Finding:
        return Finding(
            file=item.get("file", "unknown"),
            line=item.get("line"),
            severity=Severity(item.get("severity", "warning")),
            message=item["message"],
            suggestion=item.get("suggestion"),
            agent=self.name,
        )