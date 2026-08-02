"""Builds extra context around a diff.

v1: naive -- grabs the full (capped) content of each changed file. Swap
this for a tree-sitter-based implementation that extracts just the
enclosing function/class later; it only needs to keep returning a
Context object, so no other module has to change.
"""
from __future__ import annotations

from pathlib import Path

from app.schema import Context, Diff, filePath

MAX_CHARS_PER_FILE = 4000


def build_context(
        diff: Diff | None = None,
        file: filePath | None = None,
        repo_root: str = ".",
    ) -> Context:
    snippets: dict[str, str] = {}

    if diff:
        for f in diff.files:
            file_path = Path(repo_root) / f.path
            if file_path.exists():
                snippets[f.path] = file_path.read_text()[:MAX_CHARS_PER_FILE]
    elif file:
        file_path = Path(file)
        if file_path.exists():
            snippets[file] = file_path.read_text()
    return Context(snippets=snippets)
