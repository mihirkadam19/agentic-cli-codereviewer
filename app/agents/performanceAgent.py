from app.agents.baseAgent import BaseAgent


class PerformanceAgent(BaseAgent):
    name = "performance"

    SYSTEM_PROMPT = """You are a performance-focused code reviewer.
Review the given diff and surrounding context for security issues only if diff is provided.
Review the given file at the provided file path for security issues only if file path is provided.
only: N+1 queries, unnecessary loops or allocations, blocking calls in
async code, missing indexes implied by query patterns, and algorithmic
complexity problems. Ignore style, security, and general code quality.

Report findings using the report_findings tool.
"""