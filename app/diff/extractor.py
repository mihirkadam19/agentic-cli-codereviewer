"""Extracts a normalized Diff from the local git working tree.

Swapping this for a GitHub-API-based extractor (to review a PR by URL
instead of local changes) means writing a new function with the same
`-> Diff` return type. Nothing downstream needs to know the source.
"""
from __future__ import annotations

import subprocess

from app.schema import Diff, DiffFile


def get_local_diff(against: str = "HEAD") -> Diff:
    raw = subprocess.run(
        ["git", "diff", against, "--unified=3"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    files: list[DiffFile] = []
    current_path: str | None = None
    current_lines: list[str] = []

    for line in raw.splitlines():
        if line.startswith("diff --git"):
            if current_path:
                files.append(DiffFile(path=current_path, hunk="\n".join(current_lines)))
            current_path = line.split(" b/")[-1]
            current_lines = []
        else:
            current_lines.append(line)

    if current_path:
        files.append(DiffFile(path=current_path, hunk="\n".join(current_lines)))

    return Diff(files=files)
