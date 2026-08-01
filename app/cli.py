"""CLI entry point.

This is the only place that knows the full list of available agent
types. Adding a new agent means: write the class, add one line to
_AGENT_REGISTRY, and list it in .yourtool.toml. Nothing else changes.
"""
from __future__ import annotations

import asyncio

import typer

from app.config import load_config
from app.context.builder import build_context
from app.diff.extractor import get_local_diff
from app.llmClient import LLMClient
from app.orchestrator import Orchestrator
from app.output.terminal import print_findings
from app.agents.performanceAgent import PerformanceAgent
from app.agents.securityAgent import SecurityAgent
from app.agents.styleAgent import StyleAgent

cliApp = typer.Typer()

_AGENT_REGISTRY = {
    "security": SecurityAgent,
    "performance": PerformanceAgent,
    "style": StyleAgent,
}

@cliApp.callback()
def main():
    """codechk — AI-powered code review CLI."""
    pass


@cliApp.command()
def review(against: str = typer.Option("HEAD", help="Git ref to diff against")):
    """Review local uncommitted changes."""
    config = load_config()

    diff = get_local_diff(against)
    if not diff.files:
        typer.echo("No changes to review.")
        raise typer.Exit()

    context = build_context(diff)

    llm_client = LLMClient(model=config["model"])
    agents = [_AGENT_REGISTRY[name](llm_client) for name in config["agents"] if name in _AGENT_REGISTRY]

    orchestrator = Orchestrator(agents)
    findings = asyncio.run(orchestrator.run(diff, context))

    print_findings(findings)


if __name__ == "__main__":
    cliApp()
