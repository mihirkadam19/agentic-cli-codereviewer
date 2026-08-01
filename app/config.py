"""Loads .codechk.toml from the repo root.

Which agents run is config, not code -- adding a new agent to a repo's
review pipeline should never require a code change in that repo.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

DEFAULT_CONFIG = {
    "model": "claude-sonnet-4-6",
    "agents": ["security", "performance", "style"],
}


def load_config(path: str | Path = ".codechk.toml") -> dict:
    path = Path(path)
    if not path.exists():
        return DEFAULT_CONFIG

    with open(path, "rb") as f:
        user_config = tomllib.load(f)

    return {**DEFAULT_CONFIG, **user_config}
