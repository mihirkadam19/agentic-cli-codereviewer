"""LangGraph-based orchestrator. Fans out to each configured agent as a
parallel node, then merges their findings in an aggregate node."""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.baseAgent import BaseAgent
from app.llmClient import LLMClient
from app.schema import Context, Diff, filePath, Finding


class ReviewState(TypedDict, total = False):
    diff: Diff
    context: Context
    file: filePath
    findings: Annotated[list[Finding], operator.add]


def _make_agent_node(agent: BaseAgent):
    async def node(state: ReviewState) -> dict:
        try:
            result = await agent.review(
                diff=state.get("diff"), 
                context=state.get("context"), 
                file=state.get("file")
            )
        except Exception as exc:
            print(f"[warn] agent '{agent.name}' failed: {exc}")
            result = []
        return {"findings": result}
    return node


def _aggregate(state: ReviewState) -> dict:
    """Dedupe findings raised by multiple agents on the same line."""
    seen: dict[tuple[str, int | None], Finding] = {}
    for finding in state["findings"]:
        key = (finding.file, finding.line)
        seen.setdefault(key, finding)
    return {"findings": list(seen.values())}


class Orchestrator:
    def __init__(self, agents: list[BaseAgent]):
        self._agents = agents
        self._graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(ReviewState)
        builder.add_node("aggregate", _aggregate)

        for agent in self._agents:
            builder.add_node(agent.name, _make_agent_node(agent))
            builder.add_edge(START, agent.name)
            builder.add_edge(agent.name, "aggregate")

        builder.add_edge("aggregate", END)
        return builder.compile()

    async def run(self, 
                  diff: Diff | None = None, 
                  context: Context | None = None,
                  file: filePath | None = None,
                ) -> list[Finding]:

        if diff:
            result = await self._graph.ainvoke(
                {"diff": diff, "context": context, "findings": []}
            )
        elif file:
            result = await self._graph.ainvoke(
                {"file": file, "context": context, "findings": []}
            )

        return result["findings"]