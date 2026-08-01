"""Shared data models used across the review pipeline.

Every stage of the pipeline speaks these types. Agents, the orchestrator,
and output formatters never depend on each other directly -- only on
these shapes -- which is what keeps them swappable.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DiffFile(BaseModel):
    path: str
    hunk: str  # raw diff text for this file


class Diff(BaseModel):
    """Normalized representation of a set of changes."""

    files: list[DiffFile]


class Context(BaseModel):
    """Extra code context gathered around a diff (e.g. enclosing functions)."""

    snippets: dict[str, str] = Field(default_factory=dict)  # file path -> context text


class Finding(BaseModel):
    """A single issue identified by a review agent."""

    file: str
    line: int | None = None
    severity: Severity = Severity.WARNING
    message: str
    suggestion: str | None = None
    agent: str = Field(description="Name of the agent that produced this finding")
